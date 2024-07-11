from dataclasses import dataclass

from clan_cli.api import API
from clan_cli.inventory import Inventory, InventoryMeta


@dataclass
class UpdateOptions:
    directory: str
    meta: InventoryMeta


@API.register
def update_clan_meta(options: UpdateOptions) -> InventoryMeta:
    inventory = Inventory.load_file(options.directory)
    inventory.meta = options.meta

    inventory.persist(options.directory, "Update clan meta")

    return inventory.meta
