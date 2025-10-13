from dataclasses import dataclass
from typing import Any

from clan_lib.api import API
from clan_lib.flake import Flake
from clan_lib.persist.inventory_store import InventoryStore


@dataclass
class TagList:
    options: set[str]
    special: set[str]


@API.register
def list_tags(flake: Flake) -> TagList:
    """List all tags of a clan.

    Returns:
      - 'options' - Existing Tags that can be added to machines
      - 'special' - Prefined Tags that are special and cannot be added to machines, they can be used in roles and refer to a fixed set of machines.

    """
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

    global_tags = inventory_store.get_readonly_raw().get("tags", {})

    for tag in global_tags:
        if tag not in tags:
            continue

        tags.remove(tag)

    return TagList(options=tags, special=set(global_tags.keys()))
