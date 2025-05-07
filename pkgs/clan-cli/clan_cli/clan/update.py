from dataclasses import dataclass

from clan_lib.api import API

from clan_cli.inventory import Inventory, Meta, load_inventory_json, set_inventory


@dataclass
class UpdateOptions:
    directory: str
    meta: Meta


@API.register
def update_clan_meta(options: UpdateOptions) -> Inventory:
    inventory = load_inventory_json(options.directory)
    inventory["meta"] = options.meta

    set_inventory(inventory, options.directory, "Update clan metadata")

    return inventory
