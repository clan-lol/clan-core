import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from clan_lib.errors import ClanError
from clan_lib.git import commit_file
from clan_lib.nix_models.inventory import Inventory

from .util import (
    apply_patch,
    calc_patches,
    delete_by_path,
    determine_writeability,
    path_match,
)


def unwrap_known_unknown(value: Any) -> Any:
    """
    Helper untility to unwrap our custom deferred module. (uniqueDeferredSerializableModule)

    This works because we control ClanLib.type.uniqueDeferredSerializableModule

    If value is a dict with the form:
    {
        "imports": [
            {
                "_file": <any>,
                "imports": [<actual_value>]
            }
        ]
    }
    then return the actual_value.
    Otherwise, return the value unchanged.
    """
    if (
        isinstance(value, dict)
        and "imports" in value
        and isinstance(value["imports"], list)
        and len(value["imports"]) == 1
        and isinstance(value["imports"][0], dict)
        and "_file" in value["imports"][0]
        and "imports" in value["imports"][0]
        and isinstance(value["imports"][0]["imports"], list)
        and len(value["imports"][0]["imports"]) == 1
    ):
        return value["imports"][0]["imports"][0]
    return value


def sanitize(data: Any, whitelist_paths: list[str], current_path: list[str]) -> Any:
    """
    Recursively walks dicts only, unwraps matching values only on whitelisted paths.
    Throws error if a value would be transformed on non-whitelisted path.
    """
    if isinstance(data, dict):
        sanitized = {}
        for k, v in data.items():
            new_path = [*current_path, k]
            unwrapped_v = unwrap_known_unknown(v)
            if unwrapped_v is not v:  # means unwrap will happen
                # check whitelist
                wl_paths_split = [wp.split(".") for wp in whitelist_paths]
                if not path_match(new_path, wl_paths_split):
                    msg = f"Unwrap attempted at disallowed path: {'.'.join(new_path)}"
                    raise ValueError(msg)
                sanitized[k] = unwrapped_v
            else:
                sanitized[k] = sanitize(v, whitelist_paths, new_path)
        return sanitized
    return data


@dataclass
class WriteInfo:
    writeables: dict[str, set[str]]
    data_eval: Inventory
    data_disk: Inventory


class FlakeInterface(Protocol):
    def select(
        self,
        selector: str,
        nix_options: list[str] | None = None,
    ) -> Any: ...

    @property
    def path(self) -> Path: ...


class InventoryStore:
    def __init__(
        self,
        flake: FlakeInterface,
        inventory_file_name: str = "inventory.json",
        _allowed_path_transforms: list[str] | None = None,
        _keys: list[str] | None = None,
    ) -> None:
        """
        InventoryStore constructor

        :param flake: The flake to use
        :param inventory_file_name: The name of the inventory file
        :param _allowed_path_transforms: The paths where deferredModules are allowed to be transformed
        """
        self._flake = flake
        self.inventory_file = self._flake.path / inventory_file_name
        if _allowed_path_transforms is None:
            _allowed_path_transforms = [
                "instances.*.settings",
                "instances.*.machines.*.settings",
            ]
        self._allowed_path_transforms = _allowed_path_transforms

        if _keys is None:
            _keys = ["machines", "instances", "meta", "services"]
        self._keys = _keys

    def _load_merged_inventory(self) -> Inventory:
        """
        Loads the evaluated inventory.
        After all merge operations with eventual nix code in buildClan.

        Evaluates clanInternals.inventory with nix. Which is performant.

        - Contains all clan metadata
        - Contains all machines
        - and more
        """
        raw_value = self._flake.select("clanInternals.inventoryClass.inventory")
        filtered = {k: v for k, v in raw_value.items() if k in self._keys}
        sanitized = sanitize(filtered, self._allowed_path_transforms, [])

        return sanitized

    def _get_persisted(self) -> Inventory:
        """
        Load the inventory FILE from the flake directory
        If no file is found, returns an empty dictionary
        """

        # TODO: make this configurable
        if not self.inventory_file.exists():
            return {}
        with self.inventory_file.open() as f:
            try:
                res: dict = json.load(f)
                inventory = Inventory(res)  # type: ignore
            except json.JSONDecodeError as e:
                # Error decoding the inventory file
                msg = f"Error decoding inventory file: {e}"
                raise ClanError(msg) from e

        return inventory

    def _get_inventory_current_priority(self) -> dict:
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
        return self._flake.select("clanInternals.inventoryClass.introspection")

    def _write_info(self) -> WriteInfo:
        """
        Get the paths of the writeable keys in the inventory

        Load the inventory and determine the writeable keys
        Performs 2 nix evaluations to get the current priority and the inventory
        """
        current_priority = self._get_inventory_current_priority()

        data_eval: Inventory = self._load_merged_inventory()
        data_disk: Inventory = self._get_persisted()

        writeables = determine_writeability(
            current_priority, dict(data_eval), dict(data_disk)
        )

        return WriteInfo(writeables, data_eval, data_disk)

    def read(self) -> Inventory:
        """
        Accessor to the merged inventory

        Side Effects:
            Runs 'nix eval' through the '_flake' member of this class
        """
        return self._load_merged_inventory()

    def delete(self, delete_set: set[str], commit: bool = True) -> None:
        """
        Delete keys from the inventory
        """
        data_disk = dict(self._get_persisted())

        for delete_path in delete_set:
            delete_by_path(data_disk, delete_path)

        with self.inventory_file.open("w") as f:
            json.dump(data_disk, f, indent=2)

        if commit:
            commit_file(
                self.inventory_file,
                self._flake.path,
                commit_message=f"Delete inventory keys {delete_set}",
            )

    def write(self, update: Inventory, message: str, commit: bool = True) -> None:
        """
        Write the inventory to the flake directory
        and commit it to git with the given message
        """

        write_info = self._write_info()
        patchset, delete_set = calc_patches(
            dict(write_info.data_disk),
            dict(update),
            dict(write_info.data_eval),
            write_info.writeables,
        )

        persisted = dict(write_info.data_disk)
        for patch_path, data in patchset.items():
            apply_patch(persisted, patch_path, data)

        self.delete(delete_set, commit=False)

        with self.inventory_file.open("w") as f:
            json.dump(persisted, f, indent=2)

        if commit:
            commit_file(
                self.inventory_file,
                self._flake.path,
                commit_message=f"update({self.inventory_file.name}): {message}",
            )
