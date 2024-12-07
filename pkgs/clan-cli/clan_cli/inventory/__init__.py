"""
All read/write operations MUST use the inventory.

Machine data, clan data or service data can be accessed in a performant way.

This file exports stable classnames for static & dynamic type safety.

Utilize:

- load_inventory_eval: To load the actual inventory with nix declarations merged.
Operate on the returned inventory to make changes
- save_inventory: To persist changes.
"""

import contextlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from clan_cli.api import API, dataclass_to_dict, from_dict
from clan_cli.cmd import run_no_stdout
from clan_cli.errors import ClanCmdError, ClanError
from clan_cli.git import commit_file
from clan_cli.nix import nix_eval

from .classes import (
    Inventory,
    # Machine classes
    Machine,
    MachineDeploy,
    # General classes
    Meta,
    Service,
)

# Re export classes here
# This allows to renaming of classes in the generated code
__all__ = [
    "Inventory",
    "Machine",
    "MachineDeploy",
    "Meta",
    "Service",
    "dataclass_to_dict",
    "from_dict",
]


def get_inventory_path(flake_dir: str | Path, create: bool = True) -> Path:
    """
    Get the path to the inventory file in the flake directory
    """
    inventory_file = (Path(flake_dir) / "inventory.json").resolve()

    if not inventory_file.exists() and create:
        # Copy over the meta from the flake if the inventory is not initialized
        init_inventory(str(flake_dir))

    return inventory_file


# Default inventory
default_inventory: Inventory = {"meta": {"name": "New Clan"}}


@API.register
def load_inventory_eval(flake_dir: str | Path) -> Inventory:
    """
    Loads the actual inventory.
    After all merge operations with eventual nix code in buildClan.

    Evaluates clanInternals.inventory with nix. Which is performant.

    - Contains all clan metadata
    - Contains all machines
    - and more
    """
    cmd = nix_eval(
        [
            f"{flake_dir}#clanInternals.inventory",
            "--json",
        ]
    )

    proc = run_no_stdout(cmd)

    try:
        res = proc.stdout.strip()
        data = json.loads(res)
        inventory = from_dict(Inventory, data)
    except json.JSONDecodeError as e:
        msg = f"Error decoding inventory from flake: {e}"
        raise ClanError(msg) from e
    else:
        return inventory


def flatten_data(data: dict, parent_key: str = "", separator: str = ".") -> dict:
    """
    Recursively flattens a nested dictionary structure where keys are joined by the separator.

    Args:
        data (dict): The nested dictionary structure.
        parent_key (str): The current path to the nested dictionary (used for recursion).
        separator (str): The string to use for joining keys.

    Returns:
        dict: A flattened dictionary with all values. Directly in the root.
    """
    flattened = {}

    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            # Recursively flatten the nested dictionary
            flattened.update(flatten_data(value, new_key, separator))
        else:
            flattened[new_key] = value

    return flattened


def unmerge_lists(all_items: list, filter_items: list) -> list:
    """
    Unmerge the current list. Given a previous list.

    Returns:
        The other list.
    """
    # Unmerge the lists
    res = []
    for value in all_items:
        if value not in filter_items:
            res.append(value)

    return res


def find_duplicates(string_list: list[str]) -> list[str]:
    count = Counter(string_list)
    duplicates = [item for item, freq in count.items() if freq > 1]
    return duplicates


def calc_patches(
    persisted: dict, update: dict, all_values: dict, writeables: dict
) -> dict[str, Any]:
    """
    Calculate the patches to apply to the inventory.

    Given its current state and the update to apply.

    Filters out nix-values so it doesnt matter if the anyone sends them.

    : param persisted: The current state of the inventory.
    : param update: The update to apply.
    : param writeable: The writeable keys. Use 'determine_writeability'.
        Example: {'writeable': {'foo', 'foo.bar'}, 'non_writeable': {'foo.nix'}}
    : param all_values: All values in the inventory retrieved from the flake evaluation.
    """
    persisted_flat = flatten_data(persisted)
    update_flat = flatten_data(update)
    all_values_flat = flatten_data(all_values)

    patchset = {}
    for update_key, update_data in update_flat.items():
        if update_key in writeables["non_writeable"]:
            if update_data != all_values_flat.get(update_key):
                msg = f"Key '{update_key}' is not writeable."
                raise ClanError(msg)
            continue

        if update_key in writeables["writeable"]:
            if type(update_data) is not type(all_values_flat.get(update_key)):
                msg = f"Type mismatch for key '{update_key}'. Cannot update {type(all_values_flat.get(update_key))} with {type(update_data)}"
                raise ClanError(msg)

            # Handle list seperation
            if isinstance(update_data, list):
                duplicates = find_duplicates(update_data)
                if duplicates:
                    msg = f"Key '{update_key}' contains duplicates: {duplicates}. This not supported yet."
                    raise ClanError(msg)
                # List of current values
                persisted_data = persisted_flat.get(update_key, [])
                # List including nix values
                all_list = all_values_flat.get(update_key, [])
                nix_list = unmerge_lists(all_list, persisted_data)
                if update_data != all_list:
                    patchset[update_key] = unmerge_lists(update_data, nix_list)

            elif update_data != persisted_flat.get(update_key, None):
                patchset[update_key] = update_data

            continue

        if update_key not in all_values_flat:
            msg = f"Key '{update_key}' cannot be set. It does not exist."
            raise ClanError(msg)

        msg = f"Cannot determine writeability for key '{update_key}'"
        raise ClanError(msg)

    return patchset


def determine_writeability(
    priorities: dict,
    defaults: dict,
    persisted: dict,
    parent_key: str = "",
    parent_prio: int | None = None,
    results: dict | None = None,
    non_writeable: bool = False,
) -> dict:
    if results is None:
        results = {"writeable": set({}), "non_writeable": set({})}

    for key, value in priorities.items():
        if key == "__prio":
            continue

        full_key = f"{parent_key}.{key}" if parent_key else key

        # Determine the priority for the current key
        # Inherit from parent if no priority is defined
        prio = value.get("__prio", None)
        if prio is None:
            prio = parent_prio

        # If priority is less than 100, all children are not writeable
        # If the parent passed "non_writeable" earlier, this makes all children not writeable
        if (prio is not None and prio < 100) or non_writeable:
            results["non_writeable"].add(full_key)
            if isinstance(value, dict):
                determine_writeability(
                    value,
                    defaults,
                    {},  # Children won't be writeable, so correlation doesn't matter here
                    full_key,
                    prio,  # Pass the same priority down
                    results,
                    # Recursively mark all children as non-writeable
                    non_writeable=True,
                )
            continue

        # Check if the key is writeable otherwise
        key_in_correlated = key in persisted
        if prio is None:
            msg = f"Priority for key '{full_key}' is not defined. Cannot determine if it is writeable."
            raise ClanError(msg)

        is_mergeable = False
        if prio == 100:
            default = defaults.get(key)
            if isinstance(default, dict):
                is_mergeable = True
            if isinstance(default, list):
                is_mergeable = True
            if key_in_correlated:
                is_mergeable = True

        is_writeable = prio > 100 or is_mergeable

        # Append the result
        if is_writeable:
            results["writeable"].add(full_key)
        else:
            results["non_writeable"].add(full_key)

        # Recursive
        if isinstance(value, dict):
            determine_writeability(
                value,
                defaults.get(key, {}),
                persisted.get(key, {}),
                full_key,
                prio,  # Pass down current priority
                results,
            )

    return results


def get_inventory_current_priority(flake_dir: str | Path) -> dict:
    """
    Returns the current priority of the inventory values

    machines = {
        __prio = 100;
        flash-installer = {
            __prio = 100;
            deploy = {
                targetHost = { __prio = 1500; };
            };
            description = { __prio = 1500; };
            icon = { __prio = 1500; };
            name = { __prio = 1500; };
            tags = { __prio = 1500; };
        };
    }
    """
    cmd = nix_eval(
        [
            f"{flake_dir}#clanInternals.inventoryValuesPrios",
            "--json",
        ]
    )

    proc = run_no_stdout(cmd)

    try:
        res = proc.stdout.strip()
        data = json.loads(res)
    except json.JSONDecodeError as e:
        msg = f"Error decoding inventory from flake: {e}"
        raise ClanError(msg) from e
    else:
        return data


@API.register
def load_inventory_json(
    flake_dir: str | Path, default: Inventory = default_inventory
) -> Inventory:
    """
    Load the inventory file from the flake directory
    If no file is found, returns the default inventory
    """
    inventory = default

    inventory_file = get_inventory_path(flake_dir)

    with inventory_file.open() as f:
        try:
            res = json.load(f)
            inventory = from_dict(Inventory, res)
        except json.JSONDecodeError as e:
            # Error decoding the inventory file
            msg = f"Error decoding inventory file: {e}"
            raise ClanError(msg) from e

    return inventory


def patch(d: dict[str, Any], path: str, content: Any) -> None:
    """
    Update the value at a specific dot-separated path in a nested dictionary.

    If the value didn't exist before, it will be created recursively.

    :param d: The dictionary to update.
    :param path: The dot-separated path to the key (e.g., 'foo.bar').
    :param content: The new value to set.
    """
    keys = path.split(".")
    current = d
    for key in keys[:-1]:
        current = current.setdefault(key, {})
    current[keys[-1]] = content


@API.register
def patch_inventory_with(base_dir: Path, section: str, content: dict[str, Any]) -> None:
    inventory_file = get_inventory_path(base_dir)
    curr_inventory = {}
    with inventory_file.open("r") as f:
        curr_inventory = json.load(f)

    patch(curr_inventory, section, content)

    with inventory_file.open("w") as f:
        json.dump(curr_inventory, f, indent=2)

    commit_file(inventory_file, base_dir, commit_message=f"inventory.{section}: Update")


@API.register
def set_inventory(inventory: Inventory, flake_dir: str | Path, message: str) -> None:
    """
    Write the inventory to the flake directory
    and commit it to git with the given message
    """
    inventory_file = get_inventory_path(flake_dir, create=False)

    # Filter out modules not set via UI.
    # It is not possible to set modules from "/nix/store" via the UI
    modules = {}
    filtered_modules = lambda m: {
        key: value for key, value in m.items() if "/nix/store" not in value
    }
    modules = filtered_modules(inventory.get("modules", {}))  # type: ignore
    inventory["modules"] = modules

    with inventory_file.open("w") as f:
        json.dump(inventory, f, indent=2)

    commit_file(inventory_file, Path(flake_dir), commit_message=message)


def init_inventory(directory: str, init: Inventory | None = None) -> None:
    inventory = None
    # Try reading the current flake
    if init is None:
        with contextlib.suppress(ClanCmdError):
            inventory = load_inventory_eval(directory)

    if init is not None:
        inventory = init

    # Write inventory.json file
    if inventory is not None:
        # Persist creates a commit message for each change
        set_inventory(inventory, directory, "Init inventory")


@API.register
def merge_template_inventory(
    inventory: Inventory, template_inventory: Inventory, machine_name: str
) -> None:
    """
    Merge the template inventory into the current inventory
    The template inventory is expected to be a subset of the current inventory
    """
    for service_name, instance in template_inventory.get("services", {}).items():
        if len(instance.keys()) > 0:
            msg = f"Service {service_name} in template inventory has multiple instances"
            description = (
                "Only one instance per service is allowed in a template inventory"
            )
            raise ClanError(msg, description=description)

        # services.<service_name>.<instance_name>.config
        config = next((v for v in instance.values() if "config" in v), None)
        if not config:
            msg = f"Service {service_name} in template inventory has no config"
            description = "Invalid inventory configuration"
            raise ClanError(msg, description=description)

        # Disallow "config.machines" key
        if "machines" in config:
            msg = f"Service {service_name} in template inventory has machines"
            description = "The 'machines' key is not allowed in template inventory"
            raise ClanError(msg, description=description)

        # Require "config.roles" key
        if "roles" not in config:
            msg = f"Service {service_name} in template inventory has no roles"
            description = "roles key is required in template inventory"
            raise ClanError(msg, description=description)

        # TODO: Implement merging of template inventory
        msg = "Merge template inventory is not implemented yet"
        raise NotImplementedError(msg)
