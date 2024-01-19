from collections.abc import Callable
from typing import Any

from gi.repository import Gio

from clan_vm_manager.models import VM, get_initial_vms


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
