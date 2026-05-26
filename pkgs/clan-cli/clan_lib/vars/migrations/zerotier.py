import logging
from pathlib import Path

from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.git import commit_files
from clan_lib.machines.actions import list_machines
from clan_lib.services.modules import list_service_instances
from clan_lib.vars.migrations.migrate_var import (
    copy_var_file,
    delete_var_file,
    move_var_file,
)

log = logging.getLogger(__name__)

# This comment was carefully handcrafted
#
# Before this migration runs
# We can be in state "LEGACY" or "CANONICAL"
# After this migration run we are in "FINAL"
#
# - M=Machine,I=Instance,C=Controller
# - Given M: we can find I, C: via list_machines, list_service_instances
#
# LEGACY:
#
# vars/per-machine/{M}/zerotier/zerotier-identity-secret -> mv: vars/per-machine/{M}/zerotier-identity/identity-secret, cp: vars/shared/zerotier-identity-{C}/identity-secret (If is Controller)
# vars/per-machine/{C}/zerotier/zerotier-network-id -> mv: vars/shared/zerotier-network-{I}/network-id
# vars/per-machine/{M}/zerotier/zerotier-ip -> mv: vars/per-machine/{M}/zerotier-ip-{I}/ip
#
# CANONICAL:
#
# vars/shared/zerotier-controller/zerotier-identity-secret -> del. (populate fresh via the same {M}/zerotier/zerotier-identity-secret, same path a LEGACY)
# vars/shared/zerotier-controller/zerotier-network-id -> del. (populate fresh via the same {C}/zerotier/zerotier-network-id, same path a LEGACY)
# vars/shared/zerotier-controller/zerotier-ip -> del. (populate fresh via the same {M}/zerotier/zerotier-ip, same path a LEGACY)
#
# vars/per-machine/{M}/zerotier/zerotier-identity-secret -> mv: vars/per-machine/{M}/zerotier-identity/identity-secret, cp: vars/shared/zerotier-identity-{C}/identity-secret (If is Controller)
# vars/per-machine/{C}/zerotier/zerotier-network-id -> mv: vars/shared/zerotier-network-{I}/network-id
# vars/per-machine/{M}/zerotier/zerotier-ip -> mv: vars/per-machine/{M}/zerotier-ip-{I}/ip
#
# FINAL:
#
# vars/shared/zerotier-identity-{C}/identity-secret
# vars/shared/zerotier-network-{I}/network-id
# vars/per-machine/{M}/zerotier-identity/identity-secret
# vars/per-machine/{M}/zerotier-ip-{I}/ip
#
# Generator names in FINAL:
# zerotier-identity-{C} (shared)
# zerotier-network-{I} (shared)
# zerotier-identity (per-machine)
# zerotier-ip-{I} (per-machine)
#
# Verified:
#
# - LEGACY populates all paths in FINAL
# - CANONICAL populates all paths in FINAL
# - FINAL state is a no-op; making this migration idempotent and safe to run every time


def _needs_migration(clan_dir: Path) -> bool:
    """Returns true if any directories from LEGACY or CANONICAL exist"""
    if (clan_dir / "vars/shared/zerotier-controller").exists():
        return True
    per_machine = clan_dir / "vars/per-machine"
    if per_machine.is_dir():
        for machine_path in per_machine.iterdir():
            if (machine_path / "zerotier").is_dir():
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
    all_instances = list_service_instances(flake)

    network_map = {}
    for machine_name, machine in all_machines.items():
        joined = [
            (
                instance_name,
                "controller"
                if machine_name in instance.roles["controller"]["machines"]
                else "peer",
            )
            for instance_name, instance in all_instances.items()
            if (
                instance_name in machine.instance_refs
                and instance.module["name"] == "zerotier"
            )
        ]
        if not joined:
            continue

        if len(joined) > 1:
            msg = "Zerotier needs to be manually migrated.\nAutomated migration does not work if a machine is part of multiple zerotier networks"
            raise ClanError(msg)

        network_map[machine_name] = joined.pop()

    # Track changed files for git
    changed: list[Path] = []

    # 1. vars/shared/zerotier-controller
    # We can delete all vars and prune the folder.
    delete_var_file(clan_dir / "vars/shared/zerotier-controller", changed)

    shared_vars = clan_dir / "vars/shared"

    for machine_path in machine_vars_dir.iterdir():
        # Skip machines that have no zerotier
        if not (machine_path / "zerotier").exists():
            continue

        machine_name = machine_path.name

        if machine_name not in network_map:
            log.info(
                f"Removing stale zerotier vars for machine '{machine_name}' (not part of any zerotier instance in inventory)"
            )
            delete_var_file(machine_path / "zerotier", changed)
            continue

        instance, dominant_role = network_map[machine_name]

        # 1.1 cp: vars/shared/zerotier-identity-{C}/identity-secret (If is Controller)
        id_src = machine_path / "zerotier/zerotier-identity-secret"
        if dominant_role == "controller":
            copy_var_file(
                id_src,
                shared_vars / f"zerotier-identity-{machine_name}/identity-secret",
                changed,
            )
        # 1.2 mv: vars/per-machine/{M}/zerotier-identity/identity-secret
        move_var_file(
            id_src, machine_path / "zerotier-identity/identity-secret", changed
        )

        # 2. mv: vars/shared/zerotier-network-{I}/network-id
        net_src = machine_path / "zerotier/zerotier-network-id"
        move_var_file(
            net_src, shared_vars / f"zerotier-network-{instance}/network-id", changed
        )

        # 3. mv: vars/per-machine/{M}/zerotier-ip-{I}/ip
        ip_src = machine_path / "zerotier/zerotier-ip"
        move_var_file(ip_src, machine_path / f"zerotier-ip-{instance}/ip", changed)

        # 4. Remove the now-empty legacy generator directory
        old_zt = machine_path / "zerotier"
        if old_zt.exists():
            old_zt.rmdir()  # fails if migration left files behind

    commit_files(
        file_paths=changed,
        flake_dir=clan_dir,
        commit_message="automatic(zerotier-migration): upgrade vars to support multiple zerotier instances",
    )
