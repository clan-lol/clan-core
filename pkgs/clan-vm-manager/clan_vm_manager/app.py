#!/usr/bin/env python3
import argparse
from dataclasses import dataclass
from pathlib import Path

import gi
from clan_cli import vms

from clan_vm_manager.windows.flash import FlashUSBWindow

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import multiprocessing as mp

from clan_cli.clan_uri import ClanURI
from gi.repository import Gio, Gtk, Adw

from .constants import constants
from .errors.show_error import show_error_dialog
from .executor import ProcessManager
from .interfaces import Callbacks, InitialFlashValues, InitialJoinValues
from .windows.join import JoinWindow
from .windows.overview import OverviewWindow


@dataclass
class ClanWindows:
    join: type[JoinWindow]
    overview: type[OverviewWindow]
    flash_usb: type[FlashUSBWindow]


@dataclass
class ClanConfig:
    initial_window: str
    url: ClanURI | None


# Will be executed in the context of the child process
def on_except(error: Exception, proc: mp.process.BaseProcess) -> None:
    show_error_dialog(str(error))


class MainWindow(Adw.ApplicationWindow):
        def __init__(self, config: ClanConfig) -> None:
            super().__init__()
            self.set_title("Clan Manager")
            view = Adw.ToolbarView()
            header = Adw.HeaderBar()
            view.add_top_bar(header)

            label = Gtk.Label.new("testlabel")
            view.set_content(label)

            self.set_content(view)

class Application(Gtk.Application):
    def __init__(self, config: ClanConfig) -> None:
        super().__init__(
            application_id=constants["APPID"], flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        # TODO:
        # self.init_style()

        self.window = MainWindow(config)
        self.proc_manager = ProcessManager()

        self.connect("shutdown", self.on_shutdown)

    def on_shutdown(self, app: Gtk.Application) -> None:
        print("Shutting down")
        self.proc_manager.kill_all()

    def spawn_vm(self, url: str, attr: str) -> None:
        print(f"spawn_vm {url}")

        # TODO: We should use VMConfig from the history file
        vm = vms.run.inspect_vm(flake_url=url, flake_attr=attr)
        log_path = Path(".")

        # TODO: We only use the url as the ident. This is not unique as the flake_attr is missing.
        # when we migrate everything to use the ClanURI class we can use the full url as the ident
        self.proc_manager.spawn(
            ident=url,
            on_except=on_except,
            log_path=log_path,
            func=vms.run.run_vm,
            vm=vm,
        )

    def stop_vm(self, url: str, attr: str) -> None:
        self.proc_manager.kill(url)

    def running_vms(self) -> list[str]:
        return self.proc_manager.running_procs()

    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)
        Gtk.init()
        Gio.Application.do_startup(self)
        

        menu = Gio.Menu.new()
        file_menu = Gio.Menu.new()
        item = Gio.MenuItem.new("Menu Item", "app.menu_item")

        file_menu.append_item(item)
        menu.append_submenu("File", file_menu)


        # TODO: add application menu
        self.set_menubar(menu)
        


    def do_activate(self) -> None:
        win = self.props.active_window
        if not win:
            win = self.window
            win.set_application(self)
        win.present()

    # TODO: For css styling
    def init_style(self) -> None:
        pass
        # css_provider = Gtk.CssProvider()
        # css_provider.load_from_resource(constants['RESOURCEID'] + '/style.css')
        # screen = Gdk.Screen.get_default()
        # style_context = Gtk.StyleContext()
        # style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def show_join(args: argparse.Namespace) -> None:
    app = Application(
        config=ClanConfig(url=args.clan_uri, initial_window="join"),
    )
    return app.run()


def register_join_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("clan_uri", type=ClanURI, help="clan URI to join")
    parser.set_defaults(func=show_join)


def show_overview(args: argparse.Namespace) -> None:
    app = Application(
        config=ClanConfig(url=None, initial_window="overview"),
    )
    return app.run()


def register_overview_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=show_overview)