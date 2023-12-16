from collections.abc import Callable
from typing import Any

import gi

from clan_vm_manager import assets

from ..interfaces import Callbacks, InitialJoinValues

gi.require_version("Gtk", "3.0")

from gi.repository import GdkPixbuf, Gio, Gtk


class Trust(Gtk.Box):
    def __init__(self, url: str, show_next: Callable[[], None]) -> None:
        super().__init__()
        self.show_next = show_next

        icon = Gtk.Image.new_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=str(assets.loc / "placeholder.jpeg"),
                width=256,
                height=256,
                preserve_aspect_ratio=True,
            )
        )
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, expand=True)
        layout.set_border_width(20)

        upper = Gtk.Box(orientation="vertical")
        upper.set_spacing(20)
        upper.add(Gtk.Label(label="Clan URL"))
        upper.add(icon)

        self.entry = Gtk.Entry(text=str(url))
        # self.entry.set_editable(False) ?

        upper.add(self.entry)

        lower = Gtk.Box(orientation="vertical")
        lower.set_spacing(20)
        trust_button = Gtk.Button(label="Trust")
        trust_button.connect("clicked", self.on_trust)
        lower.add(trust_button)

        layout.pack_start(upper, expand=True, fill=True, padding=0)
        layout.pack_end(lower, expand=True, fill=True, padding=0)
        self.set_center_widget(layout)
        # self.show_all()

    def on_trust(self, widget: Gtk.Widget) -> None:
        print("trusted")
        print(self.entry.get_text())
        self.show_next()


class Details(Gtk.Box):
    def __init__(self, url: str, show_next: Callable[[], None]) -> None:
        super().__init__()
        self.show_next = show_next

        icon = Gtk.Image.new_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=str(assets.loc / "placeholder.jpeg"),
                width=256,
                height=256,
                preserve_aspect_ratio=True,
            )
        )
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, expand=True)
        layout.set_border_width(20)

        upper = Gtk.Box(orientation="vertical")
        upper.set_spacing(20)
        upper.add(icon)

        label = Gtk.Label(label=str(url))

        upper.add(label)

        description = Gtk.TextBuffer()
        description.set_text("Lorem ipsum")
        text_view = Gtk.TextView.new_with_buffer(description)
        text_view.set_editable(False)

        upper.add(text_view)

        lower = Gtk.Box(orientation="horizontal", expand=True)
        lower.set_spacing(20)

        layout.pack_start(upper, expand=True, fill=True, padding=0)
        layout.add(lower)

        join_button = Gtk.Button(label="Join")
        join_button.connect("clicked", self.on_join)
        layout.add(join_button)
        self.add(layout)

    def on_join(self, widget: Gtk.Widget) -> None:
        print("join")
        self.show_next()


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

        button = Gtk.ToolButton()
        button.set_icon_name("go-previous")
        button.connect("clicked", self.switch)

        toolbar = Gtk.Toolbar(orientation=Gtk.Orientation.HORIZONTAL)
        toolbar.add(button)
        vbox.add(toolbar)

        self.stack = Gtk.Stack()

        self.stack.add_titled(
            Details(str(initial_values.url), show_next=self.show_details),
            "details",
            "Details",
        )
        self.stack.add_titled(
            Trust(str(initial_values.url), show_next=self.show_details),
            "trust",
            "Trust",
        )

        vbox.add(self.stack)

        # vbox.add(Gtk.Entry(text=str(initial_values.url)))

        # Must be called AFTER all components were added
        self.show_all()

    def show_details(self) -> None:
        self.stack.set_visible_child_name("details")

    def switch(self, widget: Gtk.Widget) -> None:
        self.cbs.show_list()

    def on_quit(self, *args: Any) -> None:
        Gio.Application.quit(self.get_application())
