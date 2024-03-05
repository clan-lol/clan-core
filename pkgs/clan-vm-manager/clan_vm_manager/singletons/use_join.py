import logging
import threading
from collections.abc import Callable
from typing import Any, ClassVar

import gi
from clan_cli.clan_uri import ClanURI
from clan_cli.history.add import HistoryEntry, add_history

from clan_vm_manager.singletons.use_vms import ClanStore

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
    entry: HistoryEntry | None

    def _join_finished_task(self) -> bool:
        self.emit("join_finished", self)
        return GLib.SOURCE_REMOVE

    def __init__(self, url: ClanURI) -> None:
        super().__init__()
        self.url = url
        self.entry = None

    def __join(self) -> None:
        new_entry = add_history(self.url)
        self.entry = new_entry
        GLib.idle_add(self._join_finished_task)

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

            # Rerendering the join list every time an item changes in the clan_store
            ClanStore.use().clan_store.connect(
                "items-changed", cls._instance.on_clan_store_items_changed
            )
        return cls._instance

    def on_clan_store_items_changed(
        self, source: Any, position: int, removed: int, added: int
    ) -> None:
        self.list_store.items_changed(
            0, self.list_store.get_n_items(), self.list_store.get_n_items()
        )

    def is_empty(self) -> bool:
        return self.list_store.get_n_items() == 0

    def push(
        self, uri: ClanURI, after_join: Callable[[JoinValue, JoinValue], None]
    ) -> None:
        """
        Add a join request.
        This method can add multiple join requests if called subsequently for each request.
        """

        value = JoinValue(uri)
        if value.url.get_id() in [item.url.get_id() for item in self.list_store]:
            log.info(f"Join request already exists: {value.url}. Ignoring.")
            return

        value.connect("join_finished", self._on_join_finished)
        value.connect("join_finished", after_join)

        self.list_store.append(value)

    def _on_join_finished(self, _source: GObject.Object, value: JoinValue) -> None:
        log.info(f"Join finished: {value.url}")
        self.discard(value)
        ClanStore.use().push_history_entry(value.entry)

    def discard(self, value: JoinValue) -> None:
        (has, idx) = self.list_store.find(value)
        if has:
            self.list_store.remove(idx)
