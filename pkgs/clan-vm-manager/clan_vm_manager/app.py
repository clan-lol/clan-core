# !/usr/bin/env python3

import argparse  # noqa
from pathlib import Path  # noqa

import gi  # noqa

gi.require_version("Gtk", "3.0")  # noqa
from gi.repository import Gtk  # noqa


def start_app(args: argparse.Namespace) -> None:
    builder = Gtk.Builder()
    glade_file = Path(__file__).parent / "app.glade"
    builder.add_from_file(str(glade_file))
    window = builder.get_object("main-window")
    window.show_all()

    Gtk.main()
