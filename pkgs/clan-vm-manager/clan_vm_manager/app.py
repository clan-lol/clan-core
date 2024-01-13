#!/usr/bin/env python3
import argparse
from dataclasses import dataclass
from pathlib import Path
import os

import gi
from clan_cli import vms

from clan_vm_manager.views.list import ClanList

# from clan_vm_manager.windows.flash import FlashUSBWindow

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

import multiprocessing as mp

from clan_cli.clan_uri import ClanURI
from gi.repository import Adw, Gio, Gtk, Gdk

from .constants import constants
from .errors.show_error import show_error_dialog
from .executor import ProcessManager

# from .windows.join import JoinWindow
# from .windows.overview import OverviewWindow


@dataclass
class ClanConfig:
    initial_view: str
    url: ClanURI | None


# Will be executed in the context of the child process
def on_except(error: Exception, proc: mp.process.BaseProcess) -> None:
    show_error_dialog(str(error))


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, app: Gtk.Application, config: ClanConfig) -> None:
        super().__init__()
        self.set_application(app)

        self.set_title("Clan Manager")
        
        # ToolbarView is the root layout.
        # A Widget containing a page, as well as top and/or bottom bars.
        # See https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/class.ToolbarView.html
        self.view = Adw.ToolbarView()
        self.header = Adw.HeaderBar()
        self.view.add_top_bar(self.header)
        

        clan_list = ClanList(
            app = app
        )
        
        self.stack = Adw.ViewStack()
        self.stack.add_titled(
            clan_list, "list", "list"  
            
        )

        self.view.set_content(self.stack)

        self.set_content(self.view)


# AdwApplication
# - handles library initialization by calling adw_init() in the default GApplication::startup signal handle
# - automatically loads stylesheets (style.css, style-dark.css, ...)
# - ...
# More see: https://gnome.pages.gitlab.gnome.org/libadwaita/doc/main/class.Application.html
class Application(Adw.Application):
    def __init__(self, config: ClanConfig) -> None:
        super().__init__(
            application_id=constants["APPID"], flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.config = config
        self.proc_manager = ProcessManager()

        # self.connect("activate", self.do_activate)
        self.connect("shutdown", self.on_shutdown)
        # constants
        # breakpoint()


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
        self.init_style()
        window = MainWindow(app=self,config=self.config)
        window.set_default_size(980,650)
        window.present()
        
    # TODO: For css styling
    def init_style(self) -> None:
        resource_path = Path(__file__).parent / "style.css"
        css_provider = Gtk.CssProvider()
        css_provider.load_from_path(str(resource_path))
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def show_join(args: argparse.Namespace) -> None:
    app = Application(
        config=ClanConfig(url=args.clan_uri, initial_view="join"),
    )
    return app.run()


def register_join_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("clan_uri", type=ClanURI, help="clan URI to join")
    parser.set_defaults(func=show_join)


def show_overview(args: argparse.Namespace) -> None:
    app = Application(
        config=ClanConfig(url=None, initial_view="list"),
    )
    return app.run()


def register_overview_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=show_overview)