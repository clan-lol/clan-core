import json
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NotRequired, Protocol, TypedDict, cast

from clan_lib.errors import ClanError
from clan_lib.git import commit_file
from clan_lib.nix_models.clan import (
    Inventory,
    InventoryInstancesType,
    InventoryMachinesType,
    InventoryMetaType,
    InventoryTagsType,
)

from .util import (
    calc_patches,
    delete_by_path,
    determine_writeability,
    path_match,
    set_value_by_path,
)


def unwrap_known_unknown(value: Any) -> Any:
    """Helper untility to unwrap our custom deferred module. (uniqueDeferredSerializableModule)

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
    """Recursively walks dicts only, unwraps matching values only on whitelisted paths.
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
    data_eval: "InventorySnapshot"
    data_disk: "InventorySnapshot"


class FlakeInterface(Protocol):
    def select(self, selector: str) -> Any: ...

    def invalidate_cache(self) -> None: ...

    @property
    def path(self) -> Path: ...


class InventorySnapshot(TypedDict):
    """Restricted view of an Inventory.

    It contains only the keys that are convertible to python types and can be serialized to JSON.
    """

    machines: NotRequired[InventoryMachinesType]
    instances: NotRequired[InventoryInstancesType]
    meta: NotRequired[InventoryMetaType]
    tags: NotRequired[InventoryTagsType]


class InventoryStore:
    def __init__(
        self,
        flake: FlakeInterface,
        inventory_file_name: str = "inventory.json",
        _allowed_path_transforms: list[str] | None = None,
        _keys: list[str] | None = None,
    ) -> None:
        """InventoryStore constructor

        :param flake: The flake to use
        :param inventory_file_name: The name of the inventory file
        :param _allowed_path_transforms: The paths where deferredModules are allowed to be transformed
        """
        self._flake = flake
        self.inventory_file = self._flake.path / inventory_file_name
        if _allowed_path_transforms is None:
            _allowed_path_transforms = [
                "instances.*.roles.*.settings",
                "instances.*.roles.*.machines.*.settings",
            ]
        self._allowed_path_transforms = _allowed_path_transforms

        if _keys is None:
            _keys = list(InventorySnapshot.__annotations__.keys())

        self._keys = _keys

    def _load_merged_inventory(self) -> InventorySnapshot:
        """Loads the evaluated inventory.
        After all merge operations with eventual nix code in buildClan.

        Evaluates clanInternals.inventoryClass.inventory with nix. Which is performant.

        - Contains all clan metadata
        - Contains all machines
        - and more
        """
        raw_value = self.get_readonly_raw()
        if self._keys:
            filtered = cast(
                "InventorySnapshot",
                {k: v for k, v in raw_value.items() if k in self._keys},
            )
        else:
            filtered = cast("InventorySnapshot", raw_value)
        sanitized = sanitize(filtered, self._allowed_path_transforms, [])

        return sanitized

    def get_readonly_raw(self) -> Inventory:
        attrs = "{" + ",".join(self._keys) + "}"
        return self._flake.select(f"clanInternals.inventoryClass.inventory.{attrs}")

    def _get_persisted(self) -> InventorySnapshot:
        """Load the inventory FILE from the flake directory
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
        """Returns the current priority of the inventory values

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
        """Get the paths of the writeable keys in the inventory

        Load the inventory and determine the writeable keys
        Performs 2 nix evaluations to get the current priority and the inventory
        """
        current_priority = self._get_inventory_current_priority()

        data_eval: InventorySnapshot = self._load_merged_inventory()
        data_disk: InventorySnapshot = self._get_persisted()

        writeables = determine_writeability(
            current_priority,
            dict(data_eval),
            dict(data_disk),
        )

        return WriteInfo(writeables, data_eval, data_disk)

    def get_writeability(self) -> Any:
        """Get the writeability of the inventory

        :return: A dictionary with the writeability of all paths
        """
        write_info = self._write_info()
        return write_info.writeables

    def read(self) -> InventorySnapshot:
        """Accessor to the merged inventory

        Side Effects:
            Runs 'nix eval' through the '_flake' member of this class
        """
        return self._load_merged_inventory()

    def delete(self, delete_set: set[str], commit: bool = True) -> None:
        """Delete keys from the inventory"""
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

    def write(
        self,
        update: InventorySnapshot,
        message: str,
        commit: bool = True,
    ) -> None:
        """Write the inventory to the flake directory
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
            set_value_by_path(persisted, patch_path, data)

        for delete_path in delete_set:
            delete_by_path(persisted, delete_path)

        def post_write() -> None:
            if commit:
                commit_file(
                    self.inventory_file,
                    self._flake.path,
                    commit_message=f"update({self.inventory_file.name}): {message}",
                )

            self._flake.invalidate_cache()

        if not patchset and not delete_set:
            # No changes, no need to write
            return

        self._write(persisted, post_write=post_write)

    def _write(
        self,
        content: Any,
        post_write: Callable[[], None] | None = None,
    ) -> None:
        """Write the content to the inventory file and run post_write callback"""
        with self.inventory_file.open("w") as f:
            json.dump(content, f, indent=2)

        if post_write:
            post_write()
