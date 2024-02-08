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

from .trayicon import TrayIcon
from .windows.main_window import MainWindow

log = logging.getLogger(__name__)


class MainApplication(Adw.Application):
    __gsignals__: ClassVar = {
        "join_request": (GObject.SignalFlags.RUN_FIRST, None, [str]),
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            *args,
            application_id="lol.clan.vm.manager",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
            **kwargs,
        )
        self.tray_icon: TrayIcon | None = None

        self.add_main_option(
            "debug",
            ord("d"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "enable debug mode",
            None,
        )

        self.window: Adw.ApplicationWindow | None = None
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

        if self.tray_icon is not None:
            self.tray_icon.destroy()

        VMS.use().kill_all()

    def on_window_hide_unhide(self, *_args: Any) -> None:
        assert self.window is not None
        if self.window.is_visible():
            self.window.hide()
            return

        self.window.present()

    def dummy_menu_entry(self) -> None:
        log.info("Dummy menu entry called")

    def do_activate(self) -> None:
        self.show_window()

    def show_window(self, app: Any = None) -> None:
        if not self.window:
            self.init_style()
            self.window = MainWindow(config=ClanConfig(initial_view="list"))
            self.window.set_application(self)
            self.tray_icon = TrayIcon(self)
        self.window.present()

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
