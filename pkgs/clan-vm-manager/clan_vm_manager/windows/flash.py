from typing import Any

import gi
from clan_cli.errors import ClanError

from clan_vm_manager.errors.show_error import show_error_dialog

from ..interfaces import Callbacks, InitialFlashValues

gi.require_version("Gtk", "4.0")

from gi.repository import Gio, Gtk


class Details(Gtk.Box):
    def __init__(self, initial: InitialFlashValues, stack: Gtk.Stack) -> None:
        super().__init__()

    def on_confirm(self, widget: Gtk.Widget) -> None:
        show_error_dialog(ClanError("Feature not ready yet."), "Info")

    def on_cancel(self, widget: Gtk.Widget) -> None:
        show_error_dialog(ClanError("Feature not ready yet."), "Info")


class FlashUSBWindow(Gtk.ApplicationWindow):
    def __init__(self, cbs: Callbacks, initial_values: InitialFlashValues) -> None:
        super().__init__()
        # Initialize the main wincbsdow
        # self.cbs = cbs
        self.set_title("cLAN Manager")
        # self.connect("delete-event", self.on_quit)
        self.set_default_size(800, 600)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, )
        self.append(vbox)

        button = Gtk.ToolButton()
        button.set_icon_name("go-previous")
        button.connect("clicked", self.switch)

        # toolbar = Gtk.Toolbar(orientation=Gtk.Orientation.HORIZONTAL)
        # toolbar.add(button)
        # vbox.add(toolbar)

        self.stack = Gtk.Stack()

        print("initial_values", initial_values)
        self.stack.add_titled(
            Details(initial_values, stack=self.stack),
            "details",
            "Details",
        )

        vbox.append(self.stack)

        # Must be called AFTER all components were added
        # self.show_all()

    def switch(self, widget: Gtk.Widget) -> None:
        pass
        # self.cbs.show_list()

    def on_quit(self, *args: Any) -> None:
        Gio.Application.quit(self.get_application())
