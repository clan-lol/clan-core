import multiprocessing as mp
from typing import Any

from clan_cli.errors import ClanError
from gi.repository import Gio

from clan_vm_manager.errors.show_error import show_error_dialog
from clan_vm_manager.models import VM, get_initial_vms


# https://amolenaar.pages.gitlab.gnome.org/pygobject-docs/Adw-1/class-ToolbarView.html
# Will be executed in the context of the child process
def on_except(error: Exception, proc: mp.process.BaseProcess) -> None:
    show_error_dialog(ClanError(str(error)))


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

    def get_running_vms(self) -> list[VM]:
        return list(filter(lambda vm: vm.is_running(), self.list_store))

    def kill_all(self) -> None:
        for vm in self.get_running_vms():
            vm.stop()
