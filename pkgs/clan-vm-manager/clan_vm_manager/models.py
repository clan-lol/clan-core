import sys
import tempfile
import weakref
from enum import StrEnum
from pathlib import Path
from typing import ClassVar

import gi
from clan_cli import vms
from clan_cli.errors import ClanError
from clan_cli.history.add import HistoryEntry
from clan_cli.history.list import list_history
from gi.repository import GObject

from clan_vm_manager import assets

from .errors.show_error import show_error_dialog
from .executor import MPProcess, spawn

gi.require_version("Gtk", "4.0")
import threading

from gi.repository import GLib


class VMStatus(StrEnum):
    RUNNING = "Running"
    STOPPED = "Stopped"


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
        return self.data.flake.flake_url + self.data.flake.flake_attr

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
                icon=icon,
                status=VMStatus.STOPPED,
                data=entry,
            )
            vm_list.append(base)
    except ClanError as e:
        show_error_dialog(e)

    return vm_list
