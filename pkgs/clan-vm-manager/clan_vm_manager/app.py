#!/usr/bin/env python3
import logging
from typing import Any, ClassVar

import gi

from clan_vm_manager import assets
from clan_vm_manager.singletons.toast import InfoToast, ToastOverlay

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from clan_lib.custom_logger import setup_logging
from clan_lib.errors import ClanError
from gi.repository import Adw, Gdk, Gio, Gtk

from clan_vm_manager.components.interfaces import ClanConfig
from clan_vm_manager.singletons.use_join import GLib, GObject

from .windows.main_window import MainWindow

log = logging.getLogger(__name__)


class MainApplication(Adw.Application):
    """Initialized  every time the app is started.
    Only the Adw.ApplicationWindow is a singleton.
    So don't use any singletons  in the Adw.Application class.
    """

    __gsignals__: ClassVar = {
        "join_request": (GObject.SignalFlags.RUN_FIRST, None, [str]),
    }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        del args, kwargs  # Unused but kept for API compatibility
        super().__init__(
            application_id="org.clan.vm-manager",
            flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE,
        )

        self.add_main_option(
            "debug",
            ord("d"),
            GLib.OptionFlags.NONE,
            GLib.OptionArg.NONE,
            "enable debug mode",
            None,
        )

        self.window: MainWindow | None = None
        self.connect("activate", self.on_activate)
        self.connect("shutdown", self.on_shutdown)

    def on_shutdown(self, source: "MainApplication") -> None:
        del source  # Unused but kept for API compatibility
        log.debug("Shutting down Adw.Application")

        if self.get_windows() == []:
            log.warning("No windows to destroy")
        if self.window:
            # TODO: Doesn't seem to raise the destroy signal. Need to investigate
            # self.get_windows() returns an empty list. Desync between window and application?
            self.window.close()
            # Killing vms directly. This is dirty
            self.window.kill_vms()
        else:
            log.error("No window to destroy")

    def do_command_line(self, command_line: Any) -> int:
        options = command_line.get_options_dict()
        # convert GVariantDict -> GVariant -> dict
        options = options.end().unpack()

        if "debug" in options and self.window is None:
            setup_logging(logging.DEBUG)
        elif self.window is None:
            setup_logging(logging.INFO)
        log.debug("Debug logging enabled")

        if "debug" in options:
            ToastOverlay.use().add_toast_unique(
                InfoToast("Debug logging enabled").toast,
                "info.debugging.enabled",
            )

        args = command_line.get_arguments()

        self.activate()

        if len(args) > 1:
            uri = args[1]
            self.emit("join_request", uri)
        return 0

    def on_window_hide_unhide(self, *_args: Any) -> None:
        if not self.window:
            log.error("No window to hide/unhide")
            return
        if self.window.is_visible():
            self.window.hide()
        else:
            self.window.present()

    def dummy_menu_entry(self) -> None:
        log.info("Dummy menu entry called")

    def on_activate(self, source: "MainApplication") -> None:
        del source  # Unused but kept for API compatibility
        if not self.window:
            self.init_style()
            self.window = MainWindow(config=ClanConfig(initial_view="list"))
            self.window.set_application(self)

        self.window.show()

    # TODO: For css styling
    def init_style(self) -> None:
        resource_path = assets.loc / "style.css"

        log.debug(f"Style css path: {resource_path}")
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(str(resource_path))
        display = Gdk.Display.get_default()
        if display is None:
            msg = "Could not get default display"
            raise ClanError(msg)
        Gtk.StyleContext.add_provider_for_display(
            display,
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )
