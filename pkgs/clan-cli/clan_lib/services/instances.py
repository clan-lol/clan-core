from typing import TypedDict

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.nix_models.clan import (
    InventoryInstanceModule,
    InventoryInstanceRolesType,
    InventoryInstancesType,
    InventoryMachinesType,
)
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import set_value_by_path
from clan_lib.services.modules import (
    get_service_module,
)

# TODO: move imports out of cli/__init__.py causing import cycles
# from clan_lib.machines.actions import list_machines


@API.register
def list_service_instances(flake: Flake) -> InventoryInstancesType:
    """Returns all currently present service instances including their full configuration"""
    inventory_store = InventoryStore(flake)
    inventory = inventory_store.read()
    instances = inventory.get("instances", {})
    return instances


def collect_tags(machines: InventoryMachinesType) -> set[str]:
    res = set()
    for _, machine in machines.items():
        res |= set(machine.get("tags", []))

    return res


# Removed 'module' ref - Needs to be passed seperately
class InstanceConfig(TypedDict):
    roles: InventoryInstanceRolesType


@API.register
def create_service_instance(
    flake: Flake,
    module_ref: InventoryInstanceModule,
    instance_name: str,
    instance_config: InstanceConfig,
) -> None:
    module = get_service_module(flake, module_ref)

    inventory_store = InventoryStore(flake)
    inventory = inventory_store.read()

    instances = inventory.get("instances", {})
    if instance_name in instances:
        msg = f"service instance '{instance_name}' already exists."
        raise ClanError(msg)

    target_roles = instance_config.get("roles")
    if not target_roles:
        msg = "Creating a service instance requires adding roles"
        raise ClanError(msg)

    available_roles = set(module.get("roles", {}).keys())

    unavailable_roles = list(filter(lambda r: r not in available_roles, target_roles))
    if unavailable_roles:
        msg = f"Unknown roles: {unavailable_roles}. Use one of {available_roles}"
        raise ClanError(msg)

    role_configs = instance_config.get("roles")
    if not role_configs:
        return

    ## Validate machine references
    all_machines = inventory.get("machines", {})
    available_machine_refs = set(all_machines.keys())
    available_tag_refs = collect_tags(all_machines)

    for role_name, role_members in role_configs.items():
        machine_refs = role_members.get("machines")
        msg = f"Role: '{role_name}' - "
        if machine_refs:
            unavailable_machines = list(
                filter(lambda m: m not in available_machine_refs, machine_refs),
            )
            if unavailable_machines:
                msg += f"Unknown machine reference: {unavailable_machines}. Use one of {available_machine_refs}"
                raise ClanError(msg)

        tag_refs = role_members.get("tags")
        if tag_refs:
            unavailable_tags = list(
                filter(lambda m: m not in available_tag_refs, tag_refs),
            )

            if unavailable_tags:
                msg += (
                    f"Unknown tags: {unavailable_tags}. Use one of {available_tag_refs}"
                )
                raise ClanError(msg)

    # TODO:
    # Validate instance_config roles settings against role schema

    set_value_by_path(inventory, f"instances.{instance_name}", instance_config)
    set_value_by_path(inventory, f"instances.{instance_name}.module", module_ref)
    inventory_store.write(
        inventory,
        message=f"services: instance '{instance_name}' init",
    )
