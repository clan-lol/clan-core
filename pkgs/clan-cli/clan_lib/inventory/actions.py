from typing import TypedDict

from clan_lib.api import API
from clan_lib.flake import Flake
from clan_lib.persist.inventory_store import InventoryStore

readonly_tags = {"all", "nixos", "darwin"}


class MachineTag(TypedDict):
    name: str
    readonly: bool


@API.register
def list_inventory_tags(flake: Flake) -> list[MachineTag]:
    inventory_store = InventoryStore(flake=flake)
    inventory = inventory_store.read()

    machines = inventory.get("machines", {})

    tags: dict[str, MachineTag] = {}

    for _, machine in machines.items():
        machine_tags = machine.get("tags", [])
        for tag in machine_tags:
            tags[tag] = MachineTag(name=tag, readonly=tag in readonly_tags)

    return sorted(tags.values(), key=lambda x: x["name"])
