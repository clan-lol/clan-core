from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Adw


class Views:
    """
    This is a singleton.
    It is initialized with the first call of use()

    Usage:

    Views.use().set_visible()

    Views.use() can also be called before the data is needed. e.g. to eliminate/reduce waiting time.

    """

    _instance: "None | Views" = None
    view: Adw.ViewStack

    # Make sure the VMS class is used as a singleton
    def __init__(self) -> None:
        raise RuntimeError("Call use() instead")

    @classmethod
    def use(cls: Any) -> "Views":
        if cls._instance is None:
            print("Creating new instance")
            cls._instance = cls.__new__(cls)
            cls.view = Adw.ViewStack()

        return cls._instance
