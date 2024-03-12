import logging
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw

from clan_vm_manager.singletons.use_views import ViewStack
from clan_vm_manager.views.logs import Logs

log = logging.getLogger(__name__)


class ToastOverlay:
    """
    The ToastOverlay is a class that manages the display of toasts
    It should be used as a singleton in your application to prevent duplicate toasts
    Usage
    """

    # For some reason, the adw toast overlay cannot be subclassed
    # Thats why it is added as a class property
    overlay: Adw.ToastOverlay
    active_toasts: set[str]

    _instance: "None | ToastOverlay" = None

    def __init__(self) -> None:
        raise RuntimeError("Call use() instead")

    @classmethod
    def use(cls: Any) -> "ToastOverlay":
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls.overlay = Adw.ToastOverlay()
            cls.active_toasts = set()

        return cls._instance

    def add_toast_unique(self, toast: Adw.Toast, key: str) -> None:
        if key not in self.active_toasts:
            self.active_toasts.add(key)
            self.overlay.add_toast(toast)
            toast.connect("dismissed", lambda toast: self.active_toasts.remove(key))


class ErrorToast:
    toast: Adw.Toast

    def __init__(self, message: str) -> None:
        super().__init__()
        self.toast = Adw.Toast.new(f"Error: {message}")
        self.toast.set_priority(Adw.ToastPriority.HIGH)

        self.toast.set_button_label("details")

        views = ViewStack.use().view

        # we cannot check this type, python is not smart enough
        logs_view: Logs = views.get_child_by_name("logs")  # type: ignore
        logs_view.set_message(message)

        self.toast.connect(
            "button-clicked",
            lambda _: views.set_visible_child_name("logs"),
        )