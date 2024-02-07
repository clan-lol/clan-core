import logging
import threading
from collections.abc import Callable
from typing import Any, ClassVar

import gi
from clan_cli import ClanError
from clan_cli.clan_uri import ClanURI
from clan_cli.history.add import add_history

from clan_vm_manager.errors.show_error import show_error_dialog
from clan_vm_manager.models.use_vms import VMS, Clans

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gio, GLib, GObject

log = logging.getLogger(__name__)


class JoinValue(GObject.Object):
    # TODO: custom signals for async join

    __gsignals__: ClassVar = {
        "join_finished": (GObject.SignalFlags.RUN_FIRST, None, [GObject.Object]),
    }

    url: ClanURI

    def __init__(
        self, url: ClanURI, on_join: Callable[["JoinValue", Any], None]
    ) -> None:
        super().__init__()
        self.url = url
        self.connect("join_finished", on_join)

    def __join(self) -> None:
        add_history(self.url, all_machines=False)
        GLib.idle_add(lambda: self.emit("join_finished", self))

    def join(self) -> None:
        threading.Thread(target=self.__join).start()


class Join:
    """
    This is a singleton.
    It is initialized with the first call of use()
    """

    _instance: "None | Join" = None
    list_store: Gio.ListStore

    # Make sure the VMS class is used as a singleton
    def __init__(self) -> None:
        raise RuntimeError("Call use() instead")

    @classmethod
    def use(cls: Any) -> "Join":
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls.list_store = Gio.ListStore.new(JoinValue)

        return cls._instance

    def push(self, url: ClanURI, on_join: Callable[[JoinValue], None]) -> None:
        """
        Add a join request.
        This method can add multiple join requests if called subsequently for each request.
        """

        if url.get_id() in [item.url.get_id() for item in self.list_store]:
            log.info(f"Join request already exists: {url}")
            return

        def after_join(item: JoinValue, _: Any) -> None:
            self.discard(item)
            Clans.use().refresh()
            VMS.use().refresh()
            print("Refreshed list after join")
            on_join(item)

        self.list_store.append(JoinValue(url, after_join))

    def join(self, item: JoinValue) -> None:
        try:
            log.info(f"trying to join: {item.url}")
            item.join()
        except ClanError as e:
            show_error_dialog(e)

    def discard(self, item: JoinValue) -> None:
        (has, idx) = self.list_store.find(item)
        if has:
            self.list_store.remove(idx)
