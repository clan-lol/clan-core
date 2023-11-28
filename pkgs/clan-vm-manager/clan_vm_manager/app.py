#!/usr/bin/env python3

import argparse

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

vms = [
    ("clan://clan.lol", True, "/home/user/my-clan"),
    ("clan://lassul.lol", False, "/home/user/my-clan"),
    ("clan://mic.lol", False, "/home/user/my-clan"),
]


class MainWindow(Gtk.Window):
    def __init__(self) -> None:
        super().__init__()
        # Initialize the main window
        self.set_title("Clan VM Manager")
        self.connect("delete-event", Gtk.main_quit)

        # Some styling
        self.set_border_width(10)
        # self.set_default_size(500,300)

        # Add a notebook layout
        # https://python-gtk-3-tutorial.readthedocs.io/en/latest/layout.html#notebook
        self.notebook = Gtk.Notebook()
        self.add(self.notebook)

        vms_store = Gtk.ListStore(str, bool, str)
        for vm in vms:
            vms_store.append(list(vm))

        self.machine_tree_view = Gtk.TreeView(vms_store)
        for idx, title in enumerate(["Url", "Autostart", "Path"]):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(title, renderer, text=idx)
            col.set_sort_column_id(idx)
            self.machine_tree_view.append_column(col)

        selection = self.machine_tree_view.get_selection()
        selection.connect("changed", self.on_select_row)

        self.machine_page = Gtk.Box()
        self.machine_page.set_border_width(10)
        self.machine_page.add(self.machine_tree_view)
        self.notebook.append_page(self.machine_page, Gtk.Label(label="Overview"))

        self.join_page = Gtk.Box()
        self.join_page.set_border_width(10)
        self.join_page.add(Gtk.Label(label="Add/Join another clan"))
        self.notebook.append_page(self.join_page, Gtk.Label(label="Add/Join"))

        # Must be called AFTER all components were added
        self.show_all()

    def on_select_row(self, selection):
        model, row = selection.get_selected()
        if row is not None:
            print(f"Selected {model[row][0]}")


def start_app(args: argparse.Namespace) -> None:
    MainWindow()
    Gtk.main()
