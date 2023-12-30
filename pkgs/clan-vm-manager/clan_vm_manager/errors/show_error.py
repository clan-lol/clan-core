#!/usr/bin/env python3

from typing import Literal, Optional, Union
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from clan_cli.errors import ClanError

Severity = Union[Literal["Error"], Literal["Warning"], Literal["Info"], str]

def show_error_dialog(error: ClanError, severity: Optional[Severity] = "Error") -> None:
    message = str(error)
    dialog = Gtk.MessageDialog(None, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.CLOSE, severity)
    print("error:", message)
    dialog.format_secondary_text(message)
    dialog.run()
    dialog.destroy()
