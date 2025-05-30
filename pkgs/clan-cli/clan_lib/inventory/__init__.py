"""
DEPRECATED:

Don't use this module anymore

Instead use:
'clan_lib.persist.inventoryStore'

Which is an abstraction over the inventory

Interacting with 'clan_lib.inventory' is NOT recommended and will be removed
"""

from clan_lib.api import API
from clan_lib.flake import Flake
from clan_lib.persist.inventory_store import InventorySnapshot, InventoryStore


@API.register
def get_inventory(flake: Flake) -> InventorySnapshot:
    inventory_store = InventoryStore(flake)
    inventory = inventory_store.read()
    return inventory
