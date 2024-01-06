#!/usr/bin/env python3

from typing import Literal

import gi

gi.require_version("Gtk", "4.0")
gi.require_version('Adw', '1')
from clan_cli.errors import ClanError
from gi.repository import Gtk, Adw

Severity = Literal["Error"] | Literal["Warning"] | Literal["Info"] | str


def show_error_dialog(error: ClanError, severity: Severity | None = "Error") -> None:
    message = str(error)
    dialog = Adw.MessageDialog(
        parent=None, heading=severity, body=message
    )
    print("error:", message)
    dialog.add_response("ok", "ok")
    dialog.choose()
