from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.nix_models.inventory import (
    Machine as InventoryMachine,
)
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import set_value_by_path


@API.register
def get_machine(machine: Machine) -> InventoryMachine:
    inventory_store = InventoryStore(flake=machine.flake)
    inventory = inventory_store.read()

    machine_inv = inventory.get("machines", {}).get(machine.name)
    if machine_inv is None:
        msg = f"Machine {machine.name} not found in inventory"
        raise ClanError(msg)

    return InventoryMachine(**machine_inv)


@API.register
def update_machine(machine: Machine, update: InventoryMachine) -> None:
    assert machine.name == update.get("name", machine.name), "Machine name mismatch"
    inventory_store = InventoryStore(flake=machine.flake)
    inventory = inventory_store.read()

    set_value_by_path(inventory, f"machines.{machine.name}", update)
    inventory_store.write(
        inventory, message=f"Update information about machine {machine.name}"
    )
