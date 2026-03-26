"""Migration: rename zerotier generator to zerotier-controller for controller machines.

The zerotier service was refactored so that:
- The controller generator is now named "zerotier-controller" and is shared.
- The "zerotier" generator is only for peers.

This migration detects controller machines (those with a zerotier-network-id file)
and moves their vars from per-machine/zerotier to shared/zerotier-controller,
fixing up relative symlinks in the process.
"""

import logging
from pathlib import Path

from clan_lib.git import commit_files

log = logging.getLogger(__name__)


def _fix_symlink(symlink: Path, vars_dir: Path) -> None:
    """Rewrite a relative symlink to account for its new position under vars/.

    Symlinks use relative ../  paths to reach the clan_dir (parent of vars/).
    After moving from per-machine/{machine}/gen/... to shared/gen/...,
    the symlink is one directory level shallower, so it needs one fewer "../".

    Instead of hardcoding depths, we compute the correct number of "../"
    based on the symlink's actual position relative to vars/.
    """
    target = str(symlink.readlink())
    if not target.startswith(".."):
        return

    # Count how many ../ the old target has
    old_parts = Path(target).parts
    old_updirs = 0
    for part in old_parts:
        if part == "..":
            old_updirs += 1
        else:
            break
    suffix_parts = old_parts[old_updirs:]

    # The symlink should resolve to something relative to clan_dir (parent of vars/).
    # The number of ../ needed = depth of symlink relative to clan_dir.
    # clan_dir = vars_dir.parent
    clan_dir = vars_dir.parent
    try:
        rel = symlink.parent.relative_to(clan_dir)
    except ValueError:
        log.warning("Symlink %s is not under %s, skipping", symlink, clan_dir)
        return

    new_updirs = len(rel.parts)
    new_target = str(Path(*([".."] * new_updirs + list(suffix_parts))))
    if new_target != target:
        symlink.unlink()
        symlink.symlink_to(new_target)
        log.debug("Fixed symlink %s -> %s (was %s)", symlink, new_target, target)


def migrate_zerotier_controller(clan_dir: Path) -> None:
    """Migrate zerotier controller vars from per-machine to shared/zerotier-controller.

    Detection: a machine is the controller if it has
    vars/per-machine/{machine}/zerotier/zerotier-network-id/value

    Migration:
    1. Move vars/per-machine/{machine}/zerotier/ -> vars/shared/zerotier-controller/
    2. Fix symlinks (remove one ../ level since shared is one directory level shallower)
    """
    vars_dir = clan_dir / "vars"
    per_machine_dir = vars_dir / "per-machine"
    shared_dir = vars_dir / "shared"

    if not per_machine_dir.exists():
        return

    target_dir = shared_dir / "zerotier-controller"
    if target_dir.exists():
        # Already migrated
        return

    # Find the controller machine: the one with zerotier-network-id
    controllers: list[tuple[str, Path]] = []

    for machine_dir in per_machine_dir.iterdir():
        if not machine_dir.is_dir():
            continue
        zt_dir = machine_dir / "zerotier"
        network_id_file = zt_dir / "zerotier-network-id" / "value"
        if network_id_file.exists():
            controllers.append((machine_dir.name, zt_dir))

    if not controllers:
        return

    if len(controllers) > 1:
        names = ", ".join(name for name, _ in controllers)
        log.warning(
            "Zerotier migration: multiple machines have zerotier-network-id: %s. "
            "Cannot auto-migrate. Please manually move the controller's "
            "vars/per-machine/{machine}/zerotier/ to vars/shared/zerotier-controller/ "
            "and fix symlinks (remove one ../ level).",
            names,
        )
        return

    controller_machine, controller_src = controllers[0]

    log.info(
        "Migrating zerotier controller vars for machine '%s': %s -> %s",
        controller_machine,
        controller_src,
        target_dir,
    )

    # Collect all old files for git rm (before moving)
    old_files = [
        item
        for item in controller_src.rglob("*")
        if item.is_file() or item.is_symlink()
    ]

    # Create shared directory and move
    shared_dir.mkdir(parents=True, exist_ok=True)
    controller_src.rename(target_dir)

    # Fix symlinks: after moving one level shallower, relative ../ paths need adjusting
    for symlink in target_dir.rglob("*"):
        if symlink.is_symlink():
            _fix_symlink(symlink, vars_dir)

    # Collect all new files for git add
    new_files = [
        item for item in target_dir.rglob("*") if item.is_file() or item.is_symlink()
    ]

    # Commit the migration to git so Nix sees the new files in the store
    all_changed = old_files + new_files
    commit_files(
        all_changed,
        clan_dir,
        commit_message=f"vars: migrate zerotier controller for '{controller_machine}' from per-machine to shared",
    )

    log.info("Migration complete for zerotier controller vars.")
