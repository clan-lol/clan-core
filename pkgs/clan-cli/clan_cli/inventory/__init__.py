"""
DEPRECATED:

Don't use this module anymore

Instead use:
'clan_lib.persist.inventoryStore'

Which is an abstraction over the inventory

Interacting with 'clan_cli.inventory' is NOT recommended and will be removed
"""

import json
from pathlib import Path
from typing import Any

from clan_lib.api import API
from clan_lib.nix_models.inventory import Inventory
from clan_lib.persist.inventory_store import WriteInfo
from clan_lib.persist.util import (
    apply_patch,
    calc_patches,
    delete_by_path,
    determine_writeability,
)

from clan_cli.errors import ClanError
from clan_cli.flake import Flake
from clan_cli.git import commit_file


def get_inventory_path(flake: Flake) -> Path:
    """
    Get the path to the inventory file in the flake directory
    """
    inventory_file = (flake.path / "inventory.json").resolve()
    return inventory_file


def load_inventory_eval(flake: Flake) -> Inventory:
    """
    Loads the evaluated inventory.
    After all merge operations with eventual nix code in buildClan.

    Evaluates clanInternals.inventory with nix. Which is performant.

    - Contains all clan metadata
    - Contains all machines
    - and more
    """
    data = flake.select("clanInternals.inventory")

    try:
        inventory = Inventory(data)  # type: ignore
    except json.JSONDecodeError as e:
        msg = f"Error decoding inventory from flake: {e}"
        raise ClanError(msg) from e
    else:
        return inventory


def get_inventory_current_priority(flake: Flake) -> dict:
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

    try:
        data = flake.select("clanInternals.inventoryClass.introspection")
    except json.JSONDecodeError as e:
        msg = f"Error decoding inventory from flake: {e}"
        raise ClanError(msg) from e
    else:
        return data


@API.register
def load_inventory_json(flake: Flake) -> Inventory:
    """
    Load the inventory FILE from the flake directory
    If no file is found, returns an empty dictionary

    DO NOT USE THIS FUNCTION TO READ THE INVENTORY

    Use load_inventory_eval instead
    """

    inventory_file = get_inventory_path(flake)

    if not inventory_file.exists():
        return {}
    with inventory_file.open() as f:
        try:
            res: dict = json.load(f)
            inventory = Inventory(res)  # type: ignore
        except json.JSONDecodeError as e:
            # Error decoding the inventory file
            msg = f"Error decoding inventory file: {e}"
            raise ClanError(msg) from e

    return inventory


@API.register
def patch_inventory_with(flake: Flake, section: str, content: dict[str, Any]) -> None:
    """
    Pass only the section to update and the content to update with.
    Make sure you pass only attributes that you would like to persist.
    ATTENTION: Don't pass nix eval values unintentionally.
    """

    inventory_file = get_inventory_path(flake)

    curr_inventory = {}
    if inventory_file.exists():
        with inventory_file.open("r") as f:
            curr_inventory = json.load(f)

    apply_patch(curr_inventory, section, content)

    with inventory_file.open("w") as f:
        json.dump(curr_inventory, f, indent=2)

    commit_file(
        inventory_file, flake.path, commit_message=f"inventory.{section}: Update"
    )


@API.register
def get_inventory_with_writeable_keys(
    flake: Flake,
) -> WriteInfo:
    """
    Load the inventory and determine the writeable keys
    Performs 2 nix evaluations to get the current priority and the inventory
    """
    current_priority = get_inventory_current_priority(flake)

    data_eval: Inventory = load_inventory_eval(flake)
    data_disk: Inventory = load_inventory_json(flake)

    writeables = determine_writeability(
        current_priority, dict(data_eval), dict(data_disk)
    )

    return WriteInfo(writeables, data_eval, data_disk)


# TODO: remove this function in favor of a proper read/write API
@API.register
def set_inventory(
    inventory: Inventory, flake: Flake, message: str, commit: bool = True
) -> None:
    """
    Write the inventory to the flake directory
    and commit it to git with the given message
    """

    write_info = get_inventory_with_writeable_keys(flake)

    # Remove internals from the inventory
    inventory.pop("tags", None)  # type: ignore
    inventory.pop("options", None)  # type: ignore
    inventory.pop("assertions", None)  # type: ignore

    patchset, delete_set = calc_patches(
        dict(write_info.data_disk),
        dict(inventory),
        dict(write_info.data_eval),
        write_info.writeables,
    )
    persisted = dict(write_info.data_disk)

    for patch_path, data in patchset.items():
        apply_patch(persisted, patch_path, data)

    for delete_path in delete_set:
        delete_by_path(persisted, delete_path)

    inventory_file = get_inventory_path(flake)
    with inventory_file.open("w") as f:
        json.dump(persisted, f, indent=2)

    if commit:
        commit_file(inventory_file, flake.path, commit_message=message)


# TODO: wrap this in a proper persistence API
def delete(flake: Flake, delete_set: set[str]) -> None:
    """
    Delete keys from the inventory
    """
    write_info = get_inventory_with_writeable_keys(flake)

    data_disk = dict(write_info.data_disk)

    for delete_path in delete_set:
        delete_by_path(data_disk, delete_path)

    inventory_file = get_inventory_path(flake)
    with inventory_file.open("w") as f:
        json.dump(data_disk, f, indent=2)

    commit_file(
        inventory_file,
        flake.path,
        commit_message=f"Delete inventory keys {delete_set}",
    )


@API.register
def get_inventory(flake: Flake) -> Inventory:
    return load_inventory_eval(flake)
