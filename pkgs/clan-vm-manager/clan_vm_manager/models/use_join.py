import logging
from collections.abc import Callable
from typing import Any

import gi
from clan_cli import ClanError
from clan_cli.clan_uri import ClanURI
from clan_cli.history.add import HistoryEntry, add_history

from clan_vm_manager.errors.show_error import show_error_dialog

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gio, GObject

log = logging.getLogger(__name__)


class JoinValue(GObject.Object):
    # TODO: custom signals for async join
    # __gsignals__: ClassVar = {}

    url: ClanURI

    def __init__(self, url: ClanURI) -> None:
        super().__init__()
        self.url = url


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

    def push(self, url: ClanURI) -> None:
        """
        Add a join request.
        This method can add multiple join requests if called subsequently for each request.
        """
        self.list_store.append(JoinValue(url))

    def join(self, item: JoinValue, cb: Callable[[list[HistoryEntry]], None]) -> None:
        # TODO: remove the item that was accepted join from this list
        # and call the success function. (The caller is responsible for handling the success)
        try:
            log.info(f"trying to join: {item.url}")

            history = add_history(item.url)
            cb(history)
            self.discard(item)

        except ClanError as e:
            show_error_dialog(e)
        pass

    def discard(self, item: JoinValue) -> None:
        (has, idx) = self.list_store.find(item)
        if has:
            self.list_store.remove(idx)
