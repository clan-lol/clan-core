from dataclasses import dataclass

from clan_lib.api import API

from clan_cli.flake import Flake
from clan_cli.inventory import Inventory, Meta, load_inventory_json, set_inventory


@dataclass
class UpdateOptions:
    flake: Flake
    meta: Meta


@API.register
def update_clan_meta(options: UpdateOptions) -> Inventory:
    inventory = load_inventory_json(options.flake)
    inventory["meta"] = options.meta

    set_inventory(inventory, options.flake, "Update clan metadata")

    return inventory
