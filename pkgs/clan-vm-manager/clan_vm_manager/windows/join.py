import argparse
from typing import Any

import gi
from clan_cli.clan_uri import ClanURI

from ..app import Application

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk


class JoinWindow(Gtk.ApplicationWindow):
    def __init__(self) -> None:
        super().__init__()
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

        vbox.add(self.stack)

        # Must be called AFTER all components were added
        self.show_all()

    def on_quit(self, *args: Any) -> None:
        Gio.Application.quit(self.get_application())


def show_join(args: argparse.Namespace) -> None:
    print(f"Joining clan {args.clan_uri}")
    app = Application(JoinWindow())
    return app.run()


def register_join_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("clan_uri", type=ClanURI, help="clan URI to join")
    parser.set_defaults(func=show_join)
