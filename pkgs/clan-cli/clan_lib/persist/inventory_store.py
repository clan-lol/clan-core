import json
from dataclasses import dataclass

from clan_cli.errors import ClanError
from clan_cli.git import commit_file

from clan_lib.flake.flake import Flake
from clan_lib.nix_models.inventory import Inventory

from .util import (
    apply_patch,
    calc_patches,
    delete_by_path,
    determine_writeability,
)


@dataclass
class WriteInfo:
    writeables: dict[str, set[str]]
    data_eval: Inventory
    data_disk: Inventory


class InventoryStore:
    def __init__(
        self,
        flake: Flake,
    ) -> None:
        self._flake = flake
        self.inventory_file = self._flake.path / "inventory.json"

    def _load_merged_inventory(self) -> Inventory:
        """
        Loads the evaluated inventory.
        After all merge operations with eventual nix code in buildClan.

        Evaluates clanInternals.inventory with nix. Which is performant.

        - Contains all clan metadata
        - Contains all machines
        - and more
        """
        return self._flake.select("clanInternals.inventoryClass.inventory")

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

    def delete(self, delete_set: set[str]) -> None:
        """
        Delete keys from the inventory
        """
        write_info = self._write_info()

        data_disk = dict(write_info.data_disk)

        for delete_path in delete_set:
            delete_by_path(data_disk, delete_path)

        with self.inventory_file.open("w") as f:
            json.dump(data_disk, f, indent=2)

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

        # Remove internals from the inventory
        update.pop("tags", None)  # type: ignore
        update.pop("options", None)  # type: ignore
        update.pop("assertions", None)  # type: ignore

        patchset, delete_set = calc_patches(
            dict(write_info.data_disk),
            dict(update),
            dict(write_info.data_eval),
            write_info.writeables,
        )
        persisted = dict(write_info.data_disk)

        for patch_path, data in patchset.items():
            apply_patch(persisted, patch_path, data)

        for delete_path in delete_set:
            delete_by_path(persisted, delete_path)

        with self.inventory_file.open("w") as f:
            json.dump(persisted, f, indent=2)

        if commit:
            commit_file(
                self.inventory_file,
                self._flake.path,
                commit_message=f"update({self.inventory_file.name}): {message}",
            )
