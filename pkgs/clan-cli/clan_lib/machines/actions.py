from dataclasses import dataclass, field
from enum import StrEnum
from typing import TypedDict

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix_models.clan import (
    InventoryMachine,
)
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import (
    get_value_by_path,
    is_writeable_key,
    list_difference,
    retrieve_typed_field_names,
    set_value_by_path,
)


@dataclass
class MachineFilter:
    tags: list[str] | None = None


@dataclass
class ListOptions:
    filter: MachineFilter = field(default_factory=MachineFilter)


class MachineStatus(StrEnum):
    NOT_INSTALLED = "not_installed"
    OFFLINE = "offline"
    OUT_OF_SYNC = "out_of_sync"
    ONLINE = "online"


class MachineState(TypedDict):
    status: MachineStatus
    # add more info later when retrieving remote state


@dataclass
class MachineResponse:
    data: InventoryMachine
    # Reference the installed service instances
    instance_refs: list[str] = field(default_factory=list)


@API.register
def list_machines(
    flake: Flake,
    opts: ListOptions | None = None,
) -> dict[str, MachineResponse]:
    """List machines of a clan"""
    inventory_store = InventoryStore(flake=flake)
    inventory = inventory_store.read()

    raw_machines = inventory.get("machines", {})

    res: dict[str, MachineResponse] = {}
    for machine_name, machine in raw_machines.items():
        if opts and opts.filter.tags is not None:
            machine_tags = machine.get("tags", [])
            if all(ft in machine_tags for ft in opts.filter.tags):
                res[machine_name] = MachineResponse(data=InventoryMachine(**machine))
        else:
            res[machine_name] = MachineResponse(data=InventoryMachine(**machine))

    return res


@API.register
def get_machine(flake: Flake, name: str) -> InventoryMachine:
    """Retrieve a machine's inventory details by name from the given flake.

    Args:
        flake (Flake): The flake object representing the configuration source.
        name (str): The name of the machine to retrieve from the inventory.

    Returns:
        InventoryMachine: An instance representing the machine's inventory details.

    Raises:
        ClanError: If the machine with the specified name is not found in the clan

    """
    inventory_store = InventoryStore(flake=flake)
    inventory = inventory_store.read()

    machine_inv = inventory.get("machines", {}).get(name)
    if machine_inv is None:
        msg = f"Machine {name} does not exist"
        raise ClanError(msg)

    return InventoryMachine(**machine_inv)


@API.register
def set_machine(machine: Machine, update: InventoryMachine) -> None:
    """Update the machine information in the inventory."""
    if machine.name != update.get("name", machine.name):
        msg = "Machine name mismatch"
        raise ClanError(msg)

    inventory_store = InventoryStore(flake=machine.flake)
    inventory = inventory_store.read()

    set_value_by_path(inventory, f"machines.{machine.name}", update)
    inventory_store.write(
        inventory,
        message=f"Update information about machine {machine.name}",
    )


class FieldSchema(TypedDict):
    readonly: bool
    reason: str | None
    readonly_members: list[str]


@API.register
def get_machine_fields_schema(machine: Machine) -> dict[str, FieldSchema]:
    """Get attributes for each field of the machine.

    This function checks which fields of the 'machine' resource are readonly and provides a reason if so.

    Args:
        machine (Machine): The machine object for which to retrieve fields.

    Returns:
        dict[str, FieldSchema]: A map from field-names to { 'readonly' (bool) and 'reason' (str or None ) }

    """
    inventory_store = InventoryStore(machine.flake)
    write_info = inventory_store.get_writeability()

    field_names = retrieve_typed_field_names(InventoryMachine)

    protected_fields = {
        "name",  # name is always readonly
        "machineClass",  # machineClass can only be set during create
    }

    # TODO: handle this more generically. I.e via json schema
    persisted_data = inventory_store._get_persisted()  # noqa: SLF001
    inventory = inventory_store.read()
    all_tags = get_value_by_path(inventory, f"machines.{machine.name}.tags", [])
    persisted_tags = get_value_by_path(
        persisted_data,
        f"machines.{machine.name}.tags",
        [],
    )
    nix_tags = list_difference(all_tags, persisted_tags)

    return {
        field: {
            "readonly": (
                True
                if field in protected_fields
                else not is_writeable_key(
                    f"machines.{machine.name}.{field}",
                    write_info,
                )
            ),
            # TODO: Provide a meaningful reason
            "reason": None,
            "readonly_members": nix_tags if field == "tags" else [],
        }
        for field in field_names
    }


@API.register
def list_machine_state(flake: Flake) -> dict[str, MachineState]:
    """Retrieve the current state of all machines in the clan.

    Args:
        flake (Flake): The flake object representing the configuration source.

    """
    inventory_store = InventoryStore(flake=flake)
    inventory = inventory_store.read()

    # todo integrate with remote state when implementing https://git.clan.lol/clan/clan-core/issues/4748
    machines = inventory.get("machines", {})

    return {
        machine_name: MachineState(
            status=MachineStatus.OFFLINE
            if get_value_by_path(machine, "installedAt", None)
            else MachineStatus.NOT_INSTALLED,
        )
        for machine_name, machine in machines.items()
    }


@API.register
def get_machine_state(machine: Machine) -> MachineState:
    """Retrieve the current state of the machine.

    Args:
        machine (Machine): The machine object for which we want to retrieve the latest state.

    """
    inventory_store = InventoryStore(flake=machine.flake)
    inventory = inventory_store.read()

    # todo integrate with remote state when implementing https://git.clan.lol/clan/clan-core/issues/4748

    return MachineState(
        status=MachineStatus.OFFLINE
        if get_value_by_path(inventory, f"machines.{machine.name}.installedAt", None)
        else MachineStatus.NOT_INSTALLED,
    )
