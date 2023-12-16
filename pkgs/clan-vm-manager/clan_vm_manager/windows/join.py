from typing import Any

import gi

from ..interfaces import Callbacks, InitialJoinValues

gi.require_version("Gtk", "3.0")

from gi.repository import Gio, Gtk


class JoinWindow(Gtk.ApplicationWindow):
    def __init__(self, initial_values: InitialJoinValues, cbs: Callbacks) -> None:
        super().__init__()
        # Initialize the main wincbsdow
        self.cbs = cbs
        self.set_title("cLAN Manager")
        self.connect("delete-event", self.on_quit)
        self.set_default_size(800, 600)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, expand=True)
        self.add(vbox)

        self.stack = Gtk.Stack()

        self.stack.add_titled(Gtk.Label(str(initial_values.url)), "join", "Join")

        vbox.add(self.stack)
        vbox.add(Gtk.Entry(text=str(initial_values.url)))

        button = Gtk.Button(
            label="To List",
        )
        button.connect("clicked", self.switch)
        vbox.add(button)

        # Must be called AFTER all components were added
        self.show_all()

    def switch(self, widget: Gtk.Widget) -> None:
        self.cbs.show_list()

    def on_quit(self, *args: Any) -> None:
        Gio.Application.quit(self.get_application())
