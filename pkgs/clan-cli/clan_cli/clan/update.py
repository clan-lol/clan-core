from dataclasses import dataclass

from clan_lib.api import API
from clan_lib.flake import Flake
from clan_lib.nix_models.inventory import Inventory, Meta
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import apply_patch


@dataclass
class UpdateOptions:
    flake: Flake
    meta: Meta


@API.register
def update_clan_meta(options: UpdateOptions) -> Inventory:
    inventory_store = InventoryStore(options.flake)
    inventory = inventory_store.read()
    apply_patch(inventory, "meta", options.meta)
    inventory_store.write(inventory, message="Update clan metadata")

    return inventory
