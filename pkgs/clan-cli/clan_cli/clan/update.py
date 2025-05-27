from dataclasses import dataclass

from clan_lib.api import API
from clan_lib.flake import Flake
from clan_lib.nix_models.clan import Inventory
from clan_lib.nix_models.clan import InventoryMeta as Meta
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import set_value_by_path


@dataclass
class UpdateOptions:
    flake: Flake
    meta: Meta


@API.register
def update_clan_meta(options: UpdateOptions) -> Inventory:
    inventory_store = InventoryStore(options.flake)
    inventory = inventory_store.read()
    set_value_by_path(inventory, "meta", options.meta)
    inventory_store.write(inventory, message="Update clan metadata")

    return inventory
