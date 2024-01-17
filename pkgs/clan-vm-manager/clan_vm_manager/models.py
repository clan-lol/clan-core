import multiprocessing as mp
import sys
import weakref
from enum import StrEnum
from pathlib import Path

from clan_cli import vms
from clan_cli.errors import ClanError
from clan_cli.history.add import HistoryEntry
from clan_cli.history.list import list_history
from gi.repository import GObject

from clan_vm_manager import assets

from .errors.show_error import show_error_dialog
from .executor import MPProcess, spawn


class VMStatus(StrEnum):
    RUNNING = "Running"
    STOPPED = "Stopped"


def on_except(error: Exception, proc: mp.process.BaseProcess) -> None:
    show_error_dialog(ClanError(str(error)))


class VM(GObject.Object):
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
        self._finalizer = weakref.finalize(self, self.stop)

    def start(self) -> None:
        if self.process is not None:
            show_error_dialog(ClanError("VM is already running"))
            return
        vm = vms.run.inspect_vm(
            flake_url=self.data.flake.flake_url, flake_attr=self.data.flake.flake_attr
        )
        log_path = Path(".")

        self.process = spawn(
            on_except=on_except,
            log_path=log_path,
            func=vms.run.run_vm,
            vm=vm,
        )

    def is_running(self) -> bool:
        if self.process is not None:
            return self.process.proc.is_alive()
        return False

    def get_id(self) -> str:
        return self.data.flake.flake_url + self.data.flake.flake_attr

    def stop(self) -> None:
        if self.process is None:
            print("VM is already stopped", file=sys.stderr)
            return

        self.process.kill_group()
        self.process = None


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
