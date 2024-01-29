import sys
import tempfile
import weakref
from collections.abc import Callable
from pathlib import Path
from typing import Any, ClassVar

import gi
from clan_cli import vms
from clan_cli.errors import ClanError
from clan_cli.history.add import HistoryEntry
from clan_cli.history.list import list_history

from clan_vm_manager import assets
from clan_vm_manager.errors.show_error import show_error_dialog
from clan_vm_manager.models.interfaces import VMStatus

from .executor import MPProcess, spawn

gi.require_version("Gtk", "4.0")
import threading

from gi.repository import Gio, GLib, GObject
import logging
import multiprocessing as mp
from clan_cli.machines.machines import Machine

log = logging.getLogger(__name__)


class VM(GObject.Object):
    # Define a custom signal with the name "vm_stopped" and a string argument for the message
    __gsignals__: ClassVar = {
        "vm_status_changed": (GObject.SignalFlags.RUN_FIRST, None, [GObject.Object]),
    }

    def __init__(
        self,
        icon: Path,
        status: VMStatus,
        data: HistoryEntry,
    ) -> None:
        super().__init__()
        self.data = data
        self.process = MPProcess("dummy", mp.Process(), Path("./dummy"))
        self._watcher_id: int = 0
        self.status = status
        self._last_liveness: bool = False
        self.log_dir = tempfile.TemporaryDirectory(
            prefix="clan_vm-", suffix=f"-{self.data.flake.flake_attr}"
        )
        self._finalizer = weakref.finalize(self, self.stop)

    def __start(self) -> None:
        if self.is_running():
            log.warn("VM is already running")
            return
        machine = Machine(
            name=self.data.flake.flake_attr,
            flake=self.data.flake.flake_url,
        )
        vm = vms.run.inspect_vm(
            machine
        )
        self.process = spawn(
            on_except=None,
            log_dir=Path(str(self.log_dir.name)),
            func=vms.run.run_vm,
            vm=vm,
        )

    def start(self) -> None:
        if self.is_running():
            log.warn("VM is already running")
            return

        threading.Thread(target=self.__start).start()

        if self._watcher_id == 0:
            # Every 50ms check if the VM is still running
            self._watcher_id = GLib.timeout_add(50, self._vm_watcher_task)

            if self._watcher_id == 0:
                log.error("Failed to add watcher")
                raise ClanError("Failed to add watcher")

    def _vm_watcher_task(self) -> bool:
        if self.is_running() != self._last_liveness:
            self.emit("vm_status_changed", self)
            prev_liveness = self._last_liveness
            self._last_liveness = self.is_running()

            # If the VM was running and now it is not, remove the watcher
            if prev_liveness == True and not self.is_running():
                return GLib.SOURCE_REMOVE

        return GLib.SOURCE_CONTINUE

    def is_running(self) -> bool:
        return self.process.proc.is_alive()

    def get_id(self) -> str:
        return f"{self.data.flake.flake_url}#{self.data.flake.flake_attr}"

    def stop(self) -> None:
        log.info("Stopping VM")
        if not self.is_running():
            log.error("VM already stopped")
            return

        self.process.kill_group()

    def read_log(self) -> str:
        if not self.process.out_file.exists():
            log.error(f"Log file {self.process.out_file} does not exist")
            return ""
        return self.process.out_file.read_text()


class VMS:
    """
    This is a singleton.
    It is initialized with the first call of use()

    Usage:

    VMS.use().get_running_vms()

    VMS.use() can also be called before the data is needed. e.g. to eliminate/reduce waiting time.

    """

    list_store: Gio.ListStore
    _instance: "None | VMS" = None

    # Make sure the VMS class is used as a singleton
    def __init__(self) -> None:
        raise RuntimeError("Call use() instead")

    @classmethod
    def use(cls: Any) -> "VMS":
        if cls._instance is None:
            print("Creating new instance")
            cls._instance = cls.__new__(cls)
            cls.list_store = Gio.ListStore.new(VM)

            for vm in get_saved_vms():
                cls.list_store.append(vm)
        return cls._instance

    def filter_by_name(self, text: str) -> None:
        if text:
            filtered_list = self.list_store
            filtered_list.remove_all()
            for vm in get_saved_vms():
                if text.lower() in vm.data.flake.clan_name.lower():
                    filtered_list.append(vm)
        else:
            self.refresh()

    def get_running_vms(self) -> list[VM]:
        return list(filter(lambda vm: vm.is_running(), self.list_store))

    def kill_all(self) -> None:
        for vm in self.get_running_vms():
            vm.stop()

    def refresh(self) -> None:
        self.list_store.remove_all()
        for vm in get_saved_vms():
            self.list_store.append(vm)


def get_saved_vms() -> list[VM]:
    vm_list = []

    try:
        # Execute `clan flakes add <path>` to democlan for this to work
        for entry in list_history():
            if entry.flake.icon is None:
                icon = assets.loc / "placeholder.jpeg"
            else:
                icon = entry.flake.icon

            base = VM(
                icon=Path(icon),
                status=VMStatus.STOPPED,
                data=entry,
            )
            vm_list.append(base)
    except ClanError as e:
        show_error_dialog(e)

    return vm_list
