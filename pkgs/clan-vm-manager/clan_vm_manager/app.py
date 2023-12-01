#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Optional
from collections import OrderedDict
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk

from .constants import constants
from .ui.clan_select_list import ClanSelectPage


class VM:
    def __init__(self, icon: Path, name: str, url: str, path: Path, running: bool = False, autostart: bool = False) -> None:
        self.icon = icon.resolve()
        assert(self.icon.exists())
        assert(self.icon.is_file())
        self.url = url
        self.autostart = autostart
        self.running = running
        self.name = name
        self.path = path

    def list_display(self) -> OrderedDict[str, Any]:
        return OrderedDict({
            "Icon": str(self.icon),
            "Name": self.name,
            "URL": self.url,
            "Running": self.running,
        })


assets = Path(__file__).parent / "assets"
assert(assets.is_dir())

vms = [
    VM(assets / "cybernet.jpeg", "Cybernet Clan", "clan://cybernet.lol", "/home/user/w-clan", True),
    VM(assets / "zenith.jpeg","Zenith Clan", "clan://zenith.lol", "/home/user/lassulus-clan"),
    VM(assets / "firestorm.jpeg" ,"Firestorm Clan","clan://firestorm.lol", "/home/user/mic-clan"),
]
#vms.extend(vms)
# vms.extend(vms)
# vms.extend(vms)


class ClanJoinPage(Gtk.Box):
    def __init__(self) -> None:
        super().__init__()
        self.page = Gtk.Box()
        self.set_border_width(10)
        self.add(Gtk.Label(label="Join"))


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
        vbox.add(self.notebook)

        self.notebook.append_page(ClanSelectPage(vms), Gtk.Label(label="Overview"))
        self.notebook.append_page(ClanJoinPage(), Gtk.Label(label="Join"))

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
