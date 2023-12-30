#!/usr/bin/env python3

from typing import Literal

import gi

gi.require_version("Gtk", "3.0")
from clan_cli.errors import ClanError
from gi.repository import Gtk

Severity = Literal["Error"] | Literal["Warning"] | Literal["Info"] | str


def show_error_dialog(error: ClanError, severity: Severity | None = "Error") -> None:
    message = str(error)
    dialog = Gtk.MessageDialog(
        None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, severity
    )
    print("error:", message)
    dialog.format_secondary_text(message)
    dialog.run()
    dialog.destroy()
