#!/usr/bin/env python3

import argparse
import sys

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gio, Gtk

from typing import Any, List
from pathlib import Path
from .constants import constants

class VM():
    def __init__(self, url:str, autostart: bool, path: Path):
        self.url = url
        self.autostart = autostart
        self.path = path


vms = [
    VM("clan://clan.lol", True, "/home/user/my-clan"),
    VM("clan://lassul.lol", False, "/home/user/my-clan"),
    VM("clan://mic.lol", False, "/home/user/my-clan"),
]

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class SwitchTreeView(Gtk.ApplicationWindow):
    def __init__(self, application):
        super().__init__(application=application, title="Switch TreeView Example")
        self.set_default_size(300, 200)

        # Create a list store with two strings and a boolean
        self.liststore = Gtk.ListStore(str, str, bool)
        # Add some sample data
        self.liststore.append(["Foo", "Bar", True])
        self.liststore.append(["Baz", "Qux", False])
        self.liststore.append(["Quux", "Quuz", True])

        # Create a tree view with the list store as the model
        self.treeview = Gtk.TreeView(model=self.liststore)
        self.add(self.treeview)

        # Create a cell renderer for text
        renderer_text = Gtk.CellRendererText()

        # Create a tree view column for the first string
        column_text1 = Gtk.TreeViewColumn("Text 1", renderer_text, text=0)
        # Add the column to the tree view
        self.treeview.append_column(column_text1)

        # Create another tree view column for the second string
        column_text2 = Gtk.TreeViewColumn("Text 2", renderer_text, text=1)
        # Add the column to the tree view
        self.treeview.append_column(column_text2)

        # Create a cell renderer for toggle
        renderer_toggle = Gtk.CellRendererToggle()
        # Set the cell renderer to be activatable
        renderer_toggle.set_property("activatable", True)
        # Connect a signal handler to the toggled signal
        renderer_toggle.connect("toggled", self.on_cell_toggled)

        # Create a tree view column for the switch
        column_toggle = Gtk.TreeViewColumn("Switch", renderer_toggle, active=2)
        # Add the column to the tree view
        self.treeview.append_column(column_toggle)
        self.show_all()

    def on_cell_toggled(self, widget, path):
        # Get the current value from the model
        current_value = self.liststore[path][2]
        # Toggle the value
        self.liststore[path][2] = not current_value
        # Print the updated value
        print("Switched", path, "to", self.liststore[path][2])


class ClanSelectList(Gtk.Box):
    def __init__(self, vms):
        super().__init__()
        self.vms = vms

        self.list_store = Gtk.ListStore(str, bool, str)
        for vm in vms:
            items = list(vm.__dict__.values())
            print(f"Table: {items}")
            self.list_store.append(items)

        self.tree_view = Gtk.TreeView(self.list_store)
        for (idx, (key, value))  in enumerate(vm.__dict__.items()):
            if isinstance(value, str):
                renderer = Gtk.CellRendererText()
                col = Gtk.TreeViewColumn(key.capitalize(), renderer, text=idx)
                col.set_sort_column_id(idx)
                self.tree_view.append_column(col)
            if isinstance(value, bool):
                renderer = Gtk.CellRendererToggle()
                renderer.set_property("activatable", True)
                renderer.connect("toggled", self.on_cell_toggled)
                col = Gtk.TreeViewColumn(key.capitalize(), renderer, active=idx)
                col.set_sort_column_id(idx)
                self.tree_view.append_column(col)

        selection = self.tree_view.get_selection()
        selection.connect("changed", self.on_select_row)


        self.set_border_width(10)
        self.add(self.tree_view)

    def on_cell_toggled(self, widget, path):
        print(f"on_cell_toggled:  {path}")
        # Get the current value from the model
        current_value = self.list_store[path][1]

        print(f"current_value: {current_value}")
        # Toggle the value
        self.list_store[path][1] = not current_value
        # Print the updated value
        print("Switched", path, "to", self.list_store[path][1])


    def on_select_row(self, selection):
        model, row = selection.get_selected()
        if row is not None:
            print(f"Selected {model[row][0]}")

class ClanJoinPage(Gtk.Box):
    def __init__(self):
        super().__init__()
        self.page = Gtk.Box()
        self.set_border_width(10)
        self.add(Gtk.Label(label="Add/Join another clan"))

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        # Initialize the main window
        self.set_title("Clan VM Manager")
        self.connect("delete-event", self.on_quit)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        self.set_border_width(10)

        # Add a notebook layout
        # https://python-gtk-3-tutorial.readthedocs.io/en/latest/layout.html#notebook
        self.notebook = Gtk.Notebook()
        vbox.add(self.notebook)

        self.notebook.append_page(ClanSelectList(vms), Gtk.Label(label="Overview"))
        self.notebook.append_page(ClanJoinPage(), Gtk.Label(label="Add/Join"))

        # Must be called AFTER all components were added
        self.show_all()

    def on_quit(self, *args):
        Gio.Application.quit(self.get_application())

    def on_select_row(self, selection):
        model, row = selection.get_selected()
        if row is not None:
            print(f"Selected {model[row][0]}")


class Application(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id=constants["APPID"], flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.init_style()

    def do_startup(self):
        Gtk.Application.do_startup(self)
        Gtk.init(sys.argv)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            #win = SwitchTreeView(application=self)
            win = MainWindow(application=self)
        win.present()

    # TODO: For css styling
    def init_style(self):
        pass
        # css_provider = Gtk.CssProvider()
        # css_provider.load_from_resource(constants['RESOURCEID'] + '/style.css')
        # screen = Gdk.Screen.get_default()
        # style_context = Gtk.StyleContext()
        # style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def start_app(args: argparse.Namespace) -> None:
    app = Application()
    return app.run(sys.argv)
