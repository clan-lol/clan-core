import logging
import threading
from typing import Any, ClassVar

import gi
from clan_cli.clan_uri import ClanURI
from clan_cli.history.add import add_history

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

    def _join_finished(self) -> bool:
        self.emit("join_finished", self)
        return GLib.SOURCE_REMOVE

    def __init__(self, url: ClanURI) -> None:
        super().__init__()
        self.url = url

    def __join(self) -> None:
        add_history(self.url, all_machines=False)
        GLib.idle_add(self._join_finished)

    def join(self) -> None:
        threading.Thread(target=self.__join).start()


class JoinList:
    """
    This is a singleton.
    It is initialized with the first call of use()
    """

    _instance: "None | JoinList" = None
    list_store: Gio.ListStore

    # Make sure the VMS class is used as a singleton
    def __init__(self) -> None:
        raise RuntimeError("Call use() instead")

    @classmethod
    def use(cls: Any) -> "JoinList":
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls.list_store = Gio.ListStore.new(JoinValue)

        return cls._instance

    def is_empty(self) -> bool:
        return self.list_store.get_n_items() == 0

    def push(self, value: JoinValue) -> None:
        """
        Add a join request.
        This method can add multiple join requests if called subsequently for each request.
        """

        if value.url.get_id() in [item.url.get_id() for item in self.list_store]:
            log.info(f"Join request already exists: {value.url}")
            return

        value.connect("join_finished", self._on_join_finished)

        self.list_store.append(value)

    def _on_join_finished(self, _source: GObject.Object, value: JoinValue) -> None:
        log.info(f"Join finished: {value.url}")
        self.discard(value)

    def discard(self, value: JoinValue) -> None:
        (has, idx) = self.list_store.find(value)
        if has:
            self.list_store.remove(idx)
