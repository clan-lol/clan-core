"""Migration: remove stale `services` key from inventory.json.

Older clan versions (25.11 and earlier) wrote a `services` key into
inventory.json.  The option was removed in 26.05 — an empty `services: {}`
triggers a hard Nix eval error ('option does not exist').

This migration deletes the key when empty.  A non-empty `services` requires
manual migration to `instances`; we raise a clear error with a guide link.
"""

import logging
from typing import Any

from clan_lib.errors import ClanError

log = logging.getLogger(__name__)

_GUIDE_URL = "https://clan.lol/docs/guides/migrations/migrate-inventory-services"


def migrate_services(inventory: dict[str, Any]) -> bool:
    """Remove a stale `services` key from the inventory dict.

    Mutates *inventory* in place.

    Returns True if the dict was changed, False otherwise.
    Raises ClanError if `services` is non-empty (manual migration required).
    """
    if "services" not in inventory:
        return False

    services = inventory["services"]
    if services:
        msg = (
            "Your inventory.json contains a non-empty 'services' key from a previous clan version.\n"
            "The 'services' option has been removed. Use 'instances' instead.\n"
            f"See: {_GUIDE_URL}\n"
            "\n"
            "Please migrate your services to instances and remove the 'services' key\n"
            "from inventory.json, then re-run this command."
        )
        raise ClanError(msg)

    del inventory["services"]
    return True
