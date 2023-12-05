#!/usr/bin/env python3

import sys
from typing import Any

import gi

from .models import VMBase

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk

from .constants import constants
from .ui.clan_join_page import ClanJoinPage
from .ui.clan_select_list import ClanEdit, ClanList


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, application: Gtk.Application) -> None:
        super().__init__(application=application)
        # Initialize the main window
        self.set_title("cLAN Manager")
        self.connect("delete-event", self.on_quit)
        self.set_default_size(800, 600)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, expand=True)
        self.add(vbox)

        # Add a notebook layout
        # https://python-gtk-3-tutorial.readthedocs.io/en/latest/layout.html#notebook
        self.notebook = Gtk.Notebook()
        self.stack = Gtk.Stack()
        # self.stack_switcher = Gtk.StackSwitcher()

        self.list_hooks = {
            "remount_list": self.remount_list_view,
            "remount_edit": self.remount_edit_view,
            "set_selected": self.set_selected,
        }
        clan_list = ClanList(**self.list_hooks, selected_vm=None)  # type: ignore
        # Add named stacks
        self.stack.add_titled(clan_list, "list", "List")
        self.stack.add_titled(
            ClanJoinPage(stack=self.remount_list_view), "join", "Join"
        )
        self.stack.add_titled(
            ClanEdit(remount_list=self.remount_list_view, selected_vm=None),
            "edit",
            "Edit",
        )

        vbox.add(self.stack)

        # Must be called AFTER all components were added
        self.show_all()

    def set_selected(self, sel: VMBase | None) -> None:
        self.selected_vm = sel

        if self.selected_vm:
            print(f"APP selected + {self.selected_vm.name}")

    def remount_list_view(self) -> None:
        widget = self.stack.get_child_by_name("list")
        print("Remounting ClanListView")
        if widget:
            widget.destroy()

        clan_list = ClanList(**self.list_hooks, selected_vm=self.selected_vm)  # type: ignore
        self.stack.add_titled(clan_list, "list", "List")
        self.show_all()
        self.stack.set_visible_child_name("list")

    def remount_edit_view(self) -> None:
        print("Remounting ClanEdit")
        widget = self.stack.get_child_by_name("edit")
        if widget:
            widget.destroy()

        self.stack.add_titled(
            ClanEdit(remount_list=self.remount_list_view, selected_vm=self.selected_vm),
            "edit",
            "Edit",
        )
        self.show_all()
        self.stack.set_visible_child_name("edit")

    def on_quit(self, *args: Any) -> None:
        Gio.Application.quit(self.get_application())


class Application(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(
            application_id=constants["APPID"], flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.init_style()

    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)
        Gtk.init(sys.argv)

    def do_activate(self) -> None:
        win = self.props.active_window
        if not win:
            # win = SwitchTreeView(application=self)
            win = MainWindow(application=self)
        win.present()

    # TODO: For css styling
    def init_style(self) -> None:
        pass
        # css_provider = Gtk.CssProvider()
        # css_provider.load_from_resource(constants['RESOURCEID'] + '/style.css')
        # screen = Gdk.Screen.get_default()
        # style_context = Gtk.StyleContext()
        # style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
