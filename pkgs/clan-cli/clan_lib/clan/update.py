from dataclasses import dataclass

from clan_lib.api import API
from clan_lib.flake import Flake
from clan_lib.nix_models.clan import InventoryMeta as Meta
from clan_lib.persist.inventory_store import InventorySnapshot, InventoryStore
from clan_lib.persist.path_utils import set_value_by_path


@dataclass
class UpdateOptions:
    flake: Flake
    meta: Meta


@API.register
def set_clan_details(options: UpdateOptions) -> InventorySnapshot:
    """Update the clan metadata in the inventory of a given flake.

    Args:
        options: UpdateOptions containing the flake and the new metadata.

    Returns:
        InventorySnapshot: The updated inventory snapshot after modifying the metadata.

    Raises:
        ClanError: If the flake does not exist or if the inventory is invalid (missing the meta attribute).

    """
    inventory_store = InventoryStore(options.flake)
    inventory = inventory_store.read()
    set_value_by_path(inventory, "meta", options.meta)
    inventory_store.write(inventory, message="Update clan metadata")

    return inventory
