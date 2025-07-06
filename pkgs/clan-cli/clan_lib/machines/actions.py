from typing import TypedDict

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix_models.clan import (
    InventoryMachine,
)
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import set_value_by_path


class MachineFilter(TypedDict):
    tags: list[str]


class ListOptions(TypedDict):
    filter: MachineFilter


@API.register
def list_machines(
    flake: Flake, opts: ListOptions | None = None
) -> dict[str, InventoryMachine]:
    """
    List machines of a clan

    Usage Example:

    machines = list_machines(flake, {"filter": {"tags": ["foo" "bar"]}})

    lists only machines that include both "foo" AND "bar"

    """
    inventory_store = InventoryStore(flake=flake)
    inventory = inventory_store.read()

    machines = inventory.get("machines", {})

    if opts and opts.get("filter"):
        filtered_machines = {}
        filter_tags = opts.get("filter", {}).get("tags", [])

        for machine_name, machine in machines.items():
            machine_tags = machine.get("tags", [])
            if all(ft in machine_tags for ft in filter_tags):
                filtered_machines[machine_name] = machine

        return filtered_machines

    return machines


@API.register
def get_machine(flake: Flake, name: str) -> InventoryMachine:
    inventory_store = InventoryStore(flake=flake)
    inventory = inventory_store.read()

    machine_inv = inventory.get("machines", {}).get(name)
    if machine_inv is None:
        msg = f"Machine {name} not found in inventory"
        raise ClanError(msg)

    return InventoryMachine(**machine_inv)


@API.register
def set_machine(machine: Machine, update: InventoryMachine) -> None:
    """
    Update the machine information in the inventory.
    """
    assert machine.name == update.get("name", machine.name), "Machine name mismatch"

    inventory_store = InventoryStore(flake=machine.flake)
    inventory = inventory_store.read()

    set_value_by_path(inventory, f"machines.{machine.name}", update)
    inventory_store.write(
        inventory, message=f"Update information about machine {machine.name}"
    )
