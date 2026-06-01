import logging
from pathlib import Path

from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.git import commit_files
from clan_lib.machines.actions import list_machines
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.vars.migrations.migrate_var import (
    delete_var_file,
    move_var_file,
)

log = logging.getLogger(__name__)

# This comment was carefully handcrafted
#
# Before this migration runs
# We can be in state "LEGACY", "CANONICAL", or "OLD_FINAL"
# After this migration run we are in "FINAL"
#
# - M=Machine,I=Instance,C=Controller
# - Given M: we can find I, C: via the inventory
#
# LEGACY:
#
# vars/per-machine/{M}/zerotier/zerotier-identity-secret -> mv: vars/shared/zerotier-identity-{M}/identity-secret
# vars/per-machine/{C}/zerotier/zerotier-network-id -> mv: vars/shared/zerotier-network-{I}/network-id
# vars/per-machine/{M}/zerotier/zerotier-ip -> mv: vars/shared/zerotier-ip-{M}-{I}/ip
#
# CANONICAL:
#
# vars/shared/zerotier-controller/zerotier-identity-secret -> del. (populate fresh via LEGACY path)
# vars/shared/zerotier-controller/zerotier-network-id -> del. (populate fresh via LEGACY path)
# vars/shared/zerotier-controller/zerotier-ip -> del. (populate fresh via LEGACY path)
#
# vars/per-machine/{M}/zerotier/zerotier-identity-secret -> mv: vars/shared/zerotier-identity-{M}/identity-secret
# vars/per-machine/{C}/zerotier/zerotier-network-id -> mv: vars/shared/zerotier-network-{I}/network-id
# vars/per-machine/{M}/zerotier/zerotier-ip -> mv: vars/shared/zerotier-ip-{M}-{I}/ip
#
# OLD_FINAL (output of previous migration, before all-shared refactor):
#
# vars/shared/zerotier-identity-{C}/identity-secret -> overwritten by per-machine copy if it exists
# vars/per-machine/{M}/zerotier-identity/identity-secret -> mv: vars/shared/zerotier-identity-{M}/identity-secret (per-machine wins)
# vars/shared/zerotier-network-{I}/network-id -> already in place
# vars/per-machine/{M}/zerotier-ip-{I}/ip -> mv: vars/shared/zerotier-ip-{M}-{I}/ip
#
# FINAL (all generators shared):
#
# vars/shared/zerotier-identity-{M}/identity-secret
# vars/shared/zerotier-network-{I}/network-id
# vars/shared/zerotier-ip-{M}-{I}/ip
#
# Generator names in FINAL:
# zerotier-identity-{M} (shared) -- one per machine
# zerotier-network-{I} (shared)
# zerotier-ip-{M}-{I} (shared)
#
# Verified:
#
# - LEGACY populates all paths in FINAL
# - CANONICAL populates all paths in FINAL
# - OLD_FINAL populates all paths in FINAL
# - FINAL state is a no-op; making this migration idempotent and safe to run every time


def _needs_migration(clan_dir: Path) -> bool:
    """Returns true if any directories from LEGACY, CANONICAL, or OLD_FINAL exist"""
    if (clan_dir / "vars/shared/zerotier-controller").exists():
        return True
    per_machine = clan_dir / "vars/per-machine"
    if per_machine.is_dir():
        for machine_path in per_machine.iterdir():
            # LEGACY: old generator directory
            if (machine_path / "zerotier").is_dir():
                return True
            # OLD_FINAL: per-machine identity or IP that needs to move to shared
            if (machine_path / "zerotier-identity").is_dir():
                return True
            if any(machine_path.glob("zerotier-ip-*")):
                return True
    return False


def migrate_zerotier(clan_dir: Path) -> None:
    machine_vars_dir = clan_dir / "vars" / "per-machine"

    if not machine_vars_dir.exists():
        return

    # Shortcut if none of the directories exist, we have nothing to do.
    if not _needs_migration(clan_dir):
        return

    flake = Flake(str(clan_dir))
    all_machines = list_machines(flake)

    inventory_store = InventoryStore(flake)
    inventory = inventory_store.read()
    all_instances = inventory.get("instances", {})

    network_map = {}
    conflicts: dict[str, list[tuple[str, str]]] = {}
    for machine_name, machine in all_machines.items():
        joined = [
            (
                instance_name,
                "controller"
                if "controller" in instance["roles"]
                and machine_name in instance["roles"]["controller"]["machines"]
                else "peer",
            )
            for instance_name, instance in all_instances.items()
            if (
                instance_name in machine.instance_refs
                # Note: Every instance MUST have a module.name; (derivable from module system behavior)
                # This could conflict with downstream modules named "zerotier"
                # FIXME: list_service_instances was removed here, because it's not lazy enough, and migrations should be cheap.
                and instance["module"]["name"] == "zerotier"
            )
        ]
        if not joined:
            continue

        if len(joined) > 1:
            conflicts[machine_name] = joined
            continue

        network_map[machine_name] = joined.pop()

    if conflicts:
        lines = [
            "Automatic zerotier vars migration failed: some machines belong to multiple zerotier instances.",
            "The migration cannot determine which instance's vars directory should receive each machine's data.",
            "",
            "Affected machines:",
        ]
        for machine_name, instances in sorted(conflicts.items()):
            instance_list = ", ".join(f"{name} ({role})" for name, role in instances)
            lines.append(f"  {machine_name}: joined in {instance_list}")
        lines += [
            "",
            "To fix this, ensure each machine listed above is part of at most one zerotier",
            "instance in the inventory, then re-run the migration.",
            "After the migration completes, machines can join multiple instances.",
        ]
        raise ClanError("\n".join(lines))

    # Track changed files for git
    changed: list[Path] = []

    # 1. vars/shared/zerotier-controller
    # We can delete all vars and prune the folder.
    delete_var_file(clan_dir / "vars/shared/zerotier-controller", changed)

    shared_vars = clan_dir / "vars/shared"

    for machine_path in machine_vars_dir.iterdir():
        machine_name = machine_path.name

        # --- LEGACY / CANONICAL: migrate old generator directory ---
        if (machine_path / "zerotier").exists():
            if machine_name not in network_map:
                log.info(
                    f"Removing stale zerotier vars for machine '{machine_name}' (not part of any zerotier instance in inventory)"
                )
                delete_var_file(machine_path / "zerotier", changed)
                continue

            instance, _dominant_role = network_map[machine_name]

            # Identity -> shared (every machine, not just controllers)
            id_src = machine_path / "zerotier/zerotier-identity-secret"
            move_var_file(
                id_src,
                shared_vars / f"zerotier-identity-{machine_name}/identity-secret",
                changed,
            )

            # Network-id -> shared (unchanged destination)
            net_src = machine_path / "zerotier/zerotier-network-id"
            move_var_file(
                net_src,
                shared_vars / f"zerotier-network-{instance}/network-id",
                changed,
            )

            # IP -> shared with machine name in generator name
            ip_src = machine_path / "zerotier/zerotier-ip"
            move_var_file(
                ip_src,
                shared_vars / f"zerotier-ip-{machine_name}-{instance}/ip",
                changed,
            )

            # Remove the now-empty legacy generator directory
            old_zt = machine_path / "zerotier"
            if old_zt.exists():
                old_zt.rmdir()  # fails if migration left files behind

        # --- OLD_FINAL: migrate per-machine vars to shared ---

        # Per-machine identity -> shared identity
        # The per-machine identity is the one that was actually deployed and
        # used on the machine. For controllers, a shared copy also exists (it
        # was the generation source), but the per-machine version wins since
        # that's what the machine ran with.
        shared_identity_dst = (
            shared_vars / f"zerotier-identity-{machine_name}/identity-secret"
        )
        old_identity = machine_path / "zerotier-identity/identity-secret"
        if old_identity.exists():
            move_var_file(
                old_identity,
                shared_identity_dst,
                changed,
            )
            # Clean up empty directory
            old_id_dir = machine_path / "zerotier-identity"
            if old_id_dir.exists() and not any(old_id_dir.iterdir()):
                old_id_dir.rmdir()

        # Per-machine IP -> shared IP (need to discover instance from dir name)
        for ip_dir in sorted(machine_path.glob("zerotier-ip-*")):
            # Directory name is "zerotier-ip-{instance}"
            instance_name = ip_dir.name.removeprefix("zerotier-ip-")
            old_ip = ip_dir / "ip"
            if old_ip.exists():
                move_var_file(
                    old_ip,
                    shared_vars / f"zerotier-ip-{machine_name}-{instance_name}/ip",
                    changed,
                )
            # Clean up empty directory
            if ip_dir.exists() and not any(ip_dir.iterdir()):
                ip_dir.rmdir()

    commit_files(
        file_paths=changed,
        flake_dir=clan_dir,
        commit_message="migrate: move zerotier vars to all-shared layout",
    )
