#!/usr/bin/env python3


import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


class ClanJoinPage(Gtk.Box):
    def __init__(self, *, stack: Gtk.Stack) -> None:
        super().__init__()
        self.page = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=6, expand=True
        )
        self.set_border_width(10)
        self.stack = stack

        button = Gtk.Button(label="Back to list", margin_left=10)
        button.connect("clicked", self.switch)
        self.add(button)

        self.add(Gtk.Label("Join cLan"))

    def switch(self, widget: Gtk.Widget) -> None:
        self.stack.set_visible_child_name("list")
