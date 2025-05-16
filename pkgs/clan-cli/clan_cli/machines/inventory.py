from clan_lib.api import API
from clan_lib.nix_models.inventory import (
    Machine as InventoryMachine,
)
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import apply_patch

from clan_cli.errors import ClanError
from clan_cli.machines.machines import Machine


@API.register
def get_inv_machine(machine: Machine) -> InventoryMachine:
    inventory_store = InventoryStore(flake=machine.flake)
    inventory = inventory_store.read()

    machine_inv = inventory.get("machines", {}).get(machine.name)
    if machine_inv is None:
        msg = f"Machine {machine.name} not found in inventory"
        raise ClanError(msg)

    return InventoryMachine(**machine_inv)


@API.register
def set_inv_machine(machine: Machine, inventory_machine: InventoryMachine) -> None:
    assert machine.name == inventory_machine["name"], "Machine name mismatch"
    inventory_store = InventoryStore(flake=machine.flake)
    inventory = inventory_store.read()

    apply_patch(inventory, f"machines.{machine.name}", inventory_machine)
    inventory_store.write(
        inventory, message=f"Update information about machine {machine.name}"
    )
