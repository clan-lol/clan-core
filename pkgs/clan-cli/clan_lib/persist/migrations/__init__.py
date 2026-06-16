"""Inventory migrations that run before Nix evaluation."""

import json
import logging
from pathlib import Path

from clan_lib.git import commit_file

from .services import migrate_services

log = logging.getLogger(__name__)

_COMMIT_MESSAGE = "inventory.json: remove stale keys from previous clan version"


def run_inventory_migrations(flake_dir: Path) -> None:
    """Run all inventory.json migrations. Called before Nix evaluation.

    Reads the on-disk inventory.json, applies each migration in order,
    and writes back + commits if anything changed.
    """
    inventory_file = flake_dir / "inventory.json"
    if not inventory_file.exists():
        return

    with inventory_file.open() as f:
        try:
            inventory = json.load(f)
        except json.JSONDecodeError:
            return  # Let InventoryStore handle malformed JSON

    changed = migrate_services(inventory)

    if not changed:
        return

    with inventory_file.open("w") as f:
        json.dump(inventory, f, indent=2)

    commit_file(inventory_file, flake_dir, commit_message=_COMMIT_MESSAGE)
    log.info("Migrated inventory.json (removed stale keys)")
