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


class VM(GObject.Object):
    # Define a custom signal with the name "vm_stopped" and a string argument for the message
    __gsignals__: ClassVar = {
        "vm_started": (GObject.SignalFlags.RUN_FIRST, None, [GObject.Object]),
        "vm_stopped": (GObject.SignalFlags.RUN_FIRST, None, [GObject.Object]),
    }

    def __init__(
        self,
        icon: Path,
        status: VMStatus,
        data: HistoryEntry,
        process: MPProcess | None = None,
    ) -> None:
        super().__init__()
        self.data = data
        self.process = process
        self.status = status
        self.log_dir = tempfile.TemporaryDirectory(
            prefix="clan_vm-", suffix=f"-{self.data.flake.flake_attr}"
        )
        self._finalizer = weakref.finalize(self, self.stop)

    def start(self) -> None:
        if self.process is not None:
            show_error_dialog(ClanError("VM is already running"))
            return
        vm = vms.run.inspect_vm(
            flake_url=self.data.flake.flake_url, flake_attr=self.data.flake.flake_attr
        )
        self.process = spawn(
            on_except=None,
            log_dir=Path(str(self.log_dir.name)),
            func=vms.run.run_vm,
            vm=vm,
        )
        self.emit("vm_started", self)
        GLib.timeout_add(50, self.vm_stopped_task)

    def start_async(self) -> None:
        threading.Thread(target=self.start).start()

    def vm_stopped_task(self) -> bool:
        if not self.is_running():
            self.emit("vm_stopped", self)
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE

    def is_running(self) -> bool:
        if self.process is not None:
            return self.process.proc.is_alive()
        return False

    def get_id(self) -> str:
        return f"{self.data.flake.flake_url}#{self.data.flake.flake_attr}"

    def stop_async(self) -> None:
        threading.Thread(target=self.stop).start()

    def stop(self) -> None:
        if self.process is None:
            print("VM is already stopped", file=sys.stderr)
            return

        self.process.kill_group()
        self.process = None

    def read_log(self) -> str:
        if self.process is None:
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

            for vm in get_initial_vms():
                cls.list_store.append(vm)
        return cls._instance

    def handle_vm_stopped(self, func: Callable[[VM, VM], None]) -> None:
        for vm in self.list_store:
            vm.connect("vm_stopped", func)

    def handle_vm_started(self, func: Callable[[VM, VM], None]) -> None:
        for vm in self.list_store:
            vm.connect("vm_started", func)

    def get_running_vms(self) -> list[VM]:
        return list(filter(lambda vm: vm.is_running(), self.list_store))

    def kill_all(self) -> None:
        for vm in self.get_running_vms():
            vm.stop()

    def refresh(self) -> None:
        self.list_store.remove_all()
        for vm in get_initial_vms():
            self.list_store.append(vm)


def get_initial_vms() -> list[VM]:
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
