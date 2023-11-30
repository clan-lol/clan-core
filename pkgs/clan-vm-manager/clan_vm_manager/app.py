#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from typing import Any

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk

from .constants import constants
from .ui.clan_select_list import ClanSelectPage


class VM:
    def __init__(self, url: str, autostart: bool, path: Path) -> None:
        self.url = url
        self.autostart = autostart
        self.path = path


vms = [
    VM("clan://clan.lol", True, "/home/user/my-clan"),
    VM("clan://lassul.lol", False, "/home/user/my-clan"),
    VM("clan://mic.lol", False, "/home/user/my-clan"),
    VM("clan://dan.lol", False, "/home/user/my-clan"),
]
vms.extend(vms)
# vms.extend(vms)
# vms.extend(vms)


class ClanJoinPage(Gtk.Box):
    def __init__(self) -> None:
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

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, expand=True)
        self.add(vbox)

        # Add a notebook layout
        # https://python-gtk-3-tutorial.readthedocs.io/en/latest/layout.html#notebook
        self.notebook = Gtk.Notebook()
        vbox.add(self.notebook)

        self.notebook.append_page(ClanSelectPage(vms), Gtk.Label(label="Overview"))
        self.notebook.append_page(ClanJoinPage(), Gtk.Label(label="Add/Join"))

        # Must be called AFTER all components were added
        self.show_all()

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


def start_app(args: argparse.Namespace) -> None:
    app = Application()
    return app.run(sys.argv)
