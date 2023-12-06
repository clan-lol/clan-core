#!/usr/bin/env python3

import sys
from typing import Any

import gi

from .models import VMBase

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk

from .constants import constants
from .ui.clan_join_page import ClanJoinPage
from .ui.clan_select_list import ClanEdit, ClanList


class Application(Gtk.Application):
    def __init__(self, window: Gtk.ApplicationWindow) -> None:
        super().__init__(
            application_id=constants["APPID"], flags=Gio.ApplicationFlags.FLAGS_NONE
        )
        self.init_style()
        self.window = window

    def do_startup(self) -> None:
        Gtk.Application.do_startup(self)
        Gtk.init()

    def do_activate(self) -> None:
        win = self.props.active_window
        if not win:
           win = self.window(application=self)
        win.present()

    # TODO: For css styling
    def init_style(self) -> None:
        pass
        # css_provider = Gtk.CssProvider()
        # css_provider.load_from_resource(constants['RESOURCEID'] + '/style.css')
        # screen = Gdk.Screen.get_default()
        # style_context = Gtk.StyleContext()
        # style_context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)
