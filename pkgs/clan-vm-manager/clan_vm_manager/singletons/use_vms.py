import logging
from pathlib import Path
from typing import Any

import gi
from clan_cli.history.add import HistoryEntry

from clan_vm_manager import assets
from clan_vm_manager.components.gkvstore import GKVStore
from clan_vm_manager.components.vmobj import VMObject

gi.require_version("GObject", "2.0")
gi.require_version("Gtk", "4.0")
from gi.repository import GLib

log = logging.getLogger(__name__)


class VMStore(GKVStore):
    def __init__(self) -> None:
        super().__init__(VMObject, lambda vm: vm.data.flake.flake_attr)


class ClanStore:
    _instance: "None | ClanStore" = None
    _clan_store: GKVStore[str, VMStore]

    # Make sure the VMS class is used as a singleton
    def __init__(self) -> None:
        raise RuntimeError("Call use() instead")

    @classmethod
    def use(cls: Any) -> "ClanStore":
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._clan_store = GKVStore(
                VMStore, lambda store: store.first().data.flake.flake_url
            )

        return cls._instance

    @property
    def clan_store(self) -> GKVStore[str, VMStore]:
        return self._clan_store

    def create_vm_task(self, vm: HistoryEntry) -> bool:
        self.push_history_entry(vm)
        return GLib.SOURCE_REMOVE

    def push_history_entry(self, entry: HistoryEntry) -> None:
        # TODO: We shouldn't do this here but in the list view
        if entry.flake.icon is None:
            icon = assets.loc / "placeholder.jpeg"
        else:
            icon = entry.flake.icon

        vm = VMObject(
            icon=Path(icon),
            data=entry,
        )
        self.push(vm)

    def push(self, vm: VMObject) -> None:
        url = vm.data.flake.flake_url

        # Only write to the store if the Clan is not already in it
        # Every write to the KVStore rerenders bound widgets to the clan_store
        if url not in self.clan_store:
            log.debug(f"Creating new VMStore for {url}")
            vm_store = VMStore()
            vm_store.append(vm)
            self.clan_store[url] = vm_store
        else:
            vm_store = self.clan_store[url]
            machine = vm.data.flake.flake_attr
            old_vm = vm_store.get(machine)

            if old_vm:
                log.info(
                    f"VM {vm.data.flake.flake_attr} already exists in store. Updating data field."
                )
                old_vm.update(vm.data)
            else:
                log.debug(f"Appending VM {vm.data.flake.flake_attr} to store")
                vm_store.append(vm)

    def remove(self, vm: VMObject) -> None:
        del self.clan_store[vm.data.flake.flake_url][vm.data.flake.flake_attr]

    def get_vm(self, flake_url: str, flake_attr: str) -> None | VMObject:
        clan = self.clan_store.get(flake_url)
        if clan is None:
            return None
        return clan.get(flake_attr, None)

    def get_running_vms(self) -> list[VMObject]:
        return [
            vm
            for clan in self.clan_store.values()
            for vm in clan.values()
            if vm.is_running()
        ]

    def kill_all(self) -> None:
        for vm in self.get_running_vms():
            vm.kill()
