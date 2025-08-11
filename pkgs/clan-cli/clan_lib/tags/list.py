from typing import Any

from clan_lib.api import API
from clan_lib.flake import Flake
from clan_lib.persist.inventory_store import InventoryStore


@API.register
def list_tags(flake: Flake) -> set[str]:
    inventory_store = InventoryStore(flake=flake)
    inventory = inventory_store.read()

    machines = inventory.get("machines", {})

    tags: set[str] = set()

    for machine in machines.values():
        machine_tags = machine.get("tags", [])
        for tag in machine_tags:
            tags.add(tag)

    instances = inventory.get("instances", {})
    for instance in instances.values():
        roles: dict[str, Any] = instance.get("roles", {})
        for role in roles.values():
            role_tags = role.get("tags", {})
            for tag in role_tags:
                tags.add(tag)

    global_tags = inventory.get("tags", {})
    for tag in global_tags:
        tags.add(tag)

    return tags
