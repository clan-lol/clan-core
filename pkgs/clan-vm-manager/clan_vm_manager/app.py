#!/usr/bin/env python3
import logging
from pathlib import Path
from typing import Any

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Adw, Gdk, Gio, Gtk

from clan_vm_manager.models.interfaces import ClanConfig
from clan_vm_manager.models.use_vms import VMS

from .constants import constants
from .windows.main_window import MainWindow

log = logging.getLogger(__name__)


class MainApplication(Adw.Application):
    def __init__(self, config: ClanConfig) -> None:
        super().__init__(
            application_id=constants["APPID"], flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.config = config
        self.win: Adw.ApplicationWindow | None = None
        self.connect("shutdown", self.on_shutdown)
        self.connect("activate", self.show_window)

    def on_shutdown(self, app: Gtk.Application) -> None:
        log.debug("Shutting down")
        VMS.use().kill_all()

    def do_activate(self) -> None:
        self.show_window()

    def show_window(self, app: Any = None) -> None:
        if not self.win:
            self.init_style()
            self.win = MainWindow(config=self.config)
            self.win.set_application(self)
        self.win.present()

    # TODO: For css styling
    def init_style(self) -> None:
        resource_path = Path(__file__).parent / "style.css"
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(str(resource_path))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
