#!/usr/bin/env python3
import logging
from typing import Any, ClassVar

import gi

from clan_vm_manager import assets

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from clan_cli.custom_logger import setup_logging
from gi.repository import Adw, Gdk, Gio, Gtk

from clan_vm_manager.models.interfaces import ClanConfig
from clan_vm_manager.models.use_join import GLib, GObject
from clan_vm_manager.models.use_vms import VMS

from .windows.main_window import MainWindow

log = logging.getLogger(__name__)


class MainApplication(Adw.Application):
    __gsignals__: ClassVar = {
        "join_request": (GObject.SignalFlags.RUN_FIRST, None, [str]),
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            *args,
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs,
        )

        self.add_main_option(
            "debug",
            ord("d"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "enable debug mode",
            None,
        )

        self.win: Adw.ApplicationWindow | None = None
        self.connect("shutdown", self.on_shutdown)
        self.connect("activate", self.show_window)

    def do_command_line(self, command_line: Any) -> int:
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()

        if "debug" in options:
            setup_logging("DEBUG", root_log_name=__name__.split(".")[0])
        else:
            setup_logging("INFO", root_log_name=__name__.split(".")[0])
        log.debug("Debug logging enabled")

        args = command_line.get_arguments()

        self.activate()

        if len(args) > 1:
            log.debug(f"Join request: {args[1]}")
            uri = args[1]
            self.emit("join_request", uri)

        return 0

    def on_shutdown(self, app: Gtk.Application) -> None:
        log.debug("Shutting down")
        VMS.use().kill_all()

    def do_activate(self) -> None:
        self.show_window()

    def show_window(self, app: Any = None) -> None:
        if not self.win:
            self.init_style()
            self.win = MainWindow(config=ClanConfig(initial_view="list"))
            self.win.set_application(self)
            icon_path = assets.loc / "clan_black.png"
            self.win.set_default_icon_name(str(icon_path))
        self.win.present()

    # TODO: For css styling
    def init_style(self) -> None:
        resource_path = assets.loc / "style.css"

        log.debug(f"Style css path: {resource_path}")
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(str(resource_path))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
