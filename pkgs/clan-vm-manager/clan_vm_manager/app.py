#!/usr/bin/env python3
import argparse
from dataclasses import dataclass
from typing import Optional

import gi

gi.require_version("Gtk", "3.0")
from clan_cli.clan_uri import ClanURI
from gi.repository import Gio, Gtk

from .constants import constants
from .interfaces import Callbacks, InitialJoinValues
from .windows.join import JoinWindow
from .windows.overview import OverviewWindow


@dataclass
class ClanWindows:
   join: type[JoinWindow]
   overview: type[OverviewWindow]

@dataclass
class ClanConfig:
    initial_window: str
    url: ClanURI | None
    

class Application(Gtk.Application):
    def __init__(self, windows: ClanWindows, config: ClanConfig) -> None:
        super().__init__(
            application_id=constants["APPID"], flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.init_style()
        self.windows = windows
        initial = windows.__dict__[config.initial_window]
        
        if(issubclass(initial,JoinWindow)):
            # see JoinWindow constructor
            self.window = initial(initial_values=InitialJoinValues(url=config.url or ""), cbs=Callbacks(show_list=self.show_list, show_join=self.show_join))

        if(issubclass(initial,OverviewWindow)):
            # see OverviewWindow constructor
            self.window = initial()

    def show_list(self) -> None: 
        prev = self.window
        self.window = self.windows.__dict__["overview"]()
        self.do_activate()
        prev.hide()


    def show_join(self,initial_values: InitialJoinValues) -> None:
        prev = self.window
        self.window = self.windows.__dict__["join"]()
        self.do_activate()
        prev.hide()

    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)
        Gtk.init()

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
    print(f"Joining clan {args.clan_uri}")
    app = Application(windows=ClanWindows(join=JoinWindow, overview=OverviewWindow), config=ClanConfig(url=args.clan_uri, initial_window="join") )
    return app.run()


def register_join_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("clan_uri", type=ClanURI, help="clan URI to join")
    parser.set_defaults(func=show_join)


def show_overview(args: argparse.Namespace) -> None:
    app = Application(windows=ClanWindows(join=JoinWindow, overview=OverviewWindow), config=ClanConfig(url=None, initial_window="overview") )
    return app.run()


def register_overview_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=show_overview)
