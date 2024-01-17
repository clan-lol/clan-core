#!/usr/bin/env python3
import argparse
from dataclasses import dataclass
from pathlib import Path

import gi

from clan_vm_manager.interfaces import InitialJoinValues
from clan_vm_manager.model.use_views import Views
from clan_vm_manager.views.list import ClanList
from clan_vm_manager.views.trust_join import Trust

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from clan_cli.clan_uri import ClanURI
from gi.repository import Adw, Gdk, Gio, Gtk

from .constants import constants
from .model.use_vms import VMS


@dataclass
class ClanConfig:
    initial_view: str
    url: ClanURI | None


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, config: ClanConfig) -> None:
        super().__init__()
        self.set_title("cLAN Manager")
        self.set_default_size(980, 650)

        view = Adw.ToolbarView()
        self.set_content(view)

        header = Adw.HeaderBar()
        view.add_top_bar(header)

        # Initialize all views
        stack_view = Views.use().view
        stack_view.add_named(ClanList(), "list")
        stack_view.add_named(
            Trust(initial_values=InitialJoinValues(url=config.url)), "join.trust"
        )

        stack_view.set_visible_child_name(config.initial_view)

        clamp = Adw.Clamp()
        clamp.set_child(stack_view)
        clamp.set_maximum_size(1000)

        view.set_content(clamp)

        # Push the first page to the navigation view


class Application(Adw.Application):
    def __init__(self, config: ClanConfig) -> None:
        super().__init__(
            application_id=constants["APPID"], flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.config = config
        self.connect("shutdown", self.on_shutdown)

    def on_shutdown(self, app: Gtk.Application) -> None:
        print("Shutting down")
        VMS.use().kill_all()

    def do_activate(self) -> None:
        self.init_style()
        window = MainWindow(config=self.config)
        window.set_application(self)
        window.present()

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


def show_join(args: argparse.Namespace) -> None:
    app = Application(
        config=ClanConfig(url=args.clan_uri, initial_view="join.trust"),
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
