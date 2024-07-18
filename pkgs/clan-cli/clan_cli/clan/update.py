from dataclasses import dataclass

from clan_cli.api import API
from clan_cli.inventory import Meta, load_inventory, save_inventory


@dataclass
class UpdateOptions:
    directory: str
    meta: Meta


@API.register
def update_clan_meta(options: UpdateOptions) -> Meta:
    inventory = load_inventory(options.directory)
    inventory.meta = options.meta

    save_inventory(inventory, options.directory, "Update clan metadata")

    return inventory.meta
