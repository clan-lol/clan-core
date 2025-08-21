import logging

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.nix_models.clan import InventoryMeta
from clan_lib.persist.inventory_store import InventoryStore

log = logging.getLogger(__name__)


@API.register
def get_clan_details(flake: Flake) -> InventoryMeta:
    """Retrieve the clan details from the inventory of a given flake.
    Args:
        flake: The Flake instance representing the clan.
    Returns:
        InventoryMeta: The meta information from the clan's inventory.
    Raises:
        ClanError: If the flake does not exist, or if the inventory is invalid (missing the meta attribute).
    """
    inventory_store = InventoryStore(flake)
    inventory = inventory_store.read()

    meta = inventory.get("meta")
    if not meta:
        msg = f"Inventory of flake '{flake}' does not have a meta attribute"
        raise ClanError(msg)

    return meta
