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
    is_writeable_key,
    retrieve_typed_field_names,
    set_value_by_path,
    unmerge_lists,
)


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
    """
    Retrieve a machine's inventory details by name from the given flake.

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


class FieldSchema(TypedDict):
    readonly: bool
    reason: str | None
    readonly_members: list[str]


@API.register
def get_machine_fields_schema(machine: Machine) -> dict[str, FieldSchema]:
    """
    Get attributes for each field of the machine.

    This function checks which fields of the 'machine' resource are readonly and provides a reason if so.

    Args:
        machine (Machine): The machine object for which to retrieve fields.

    Returns:
        dict[str, FieldSchema]: A map from field-names to { 'readonly' (bool) and 'reason' (str or None ) }
    """

    inventory_store = InventoryStore(machine.flake)
    write_info = inventory_store.get_writeability_of(f"machines.{machine.name}")

    field_names = retrieve_typed_field_names(InventoryMachine)

    protected_fields = {
        "name",  # name is always readonly
        "machineClass",  # machineClass can only be set during create
    }

    # TODO: handle this more generically. I.e via json schema
    persisted_data = inventory_store._get_persisted()  # noqa: SLF001
    inventory = inventory_store.read()  #
    all_tags = inventory.get("machines", {}).get(machine.name, {}).get("tags", [])
    persisted_tags = (
        persisted_data.get("machines", {}).get(machine.name, {}).get("tags", [])
    )
    nix_tags = unmerge_lists(all_tags, persisted_tags)

    return {
        field: {
            "readonly": (
                True
                if field in protected_fields
                else not is_writeable_key(
                    f"machines.{machine.name}.{field}", write_info
                )
            ),
            # TODO: Provide a meaningful reason
            "reason": None,
            "readonly_members": nix_tags if field == "tags" else [],
        }
        for field in field_names
    }
