from dataclasses import dataclass

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.nix_models.clan import (
    InventoryMachine,
)
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import set_value_by_path


@API.register
def list_machines(flake: Flake) -> dict[str, InventoryMachine]:
    """
    List machines in the inventory for the UI.
    """
    inventory_store = InventoryStore(flake=flake)
    inventory = inventory_store.read()

    machines = inventory.get("machines", {})
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


# TODO: remove this machine, once the Machine class is refactored
# We added this now, to allow for dispatching actions. To require only 'name' and 'flake' of a machine.
@dataclass(frozen=True)
class MachineID:
    name: str
    flake: Flake


@API.register
def set_machine(machine: MachineID, update: InventoryMachine) -> None:
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
