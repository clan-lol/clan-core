#!/usr/bin/env python3

import argparse
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk

glade_dir = Path(__file__).parent


#
# 1. our .glade file (may contain paths)
#
@Gtk.Template.from_file(glade_dir / "app.glade")
class AppWindow(Gtk.ApplicationWindow):
    #
    # 2. the GtkApplicationWindow class
    #
    __gtype_name__ = "main-window"

    #
    # 3. the Button name we saved above
    #
    help_button: Gtk.Button = Gtk.Template.Child()
    next_button: Gtk.Button = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def onDestroy(self, _):
        Gio.Application.quit(self.get_application())

    #
    # 4. the signal handler name we saved above
    #
    @Gtk.Template.Callback()
    def onButtonPressed(self, widget, **_kwargs):
        assert self.help_button == widget
        print(widget.get_label())

    @Gtk.Template.Callback()
    def onNextButtonPressed(self, widget, **_kwargs):
        assert self.next_button == widget
        # Hide the first window
        self.hide()

        # Show the second window
        self.get_application().window2.show_all()


# Decorate the second window class with the template
@Gtk.Template.from_file(glade_dir / "second.glade")
class SecondWindow(Gtk.ApplicationWindow):
    #
    # the GtkApplicationWindow class
    #
    __gtype_name__ = "second-window"

    # import the button from the template with name 'back_button'
    back_button: Gtk.Button = Gtk.Template.Child()

    @Gtk.Template.Callback()
    def onDestroy(self, _):
        Gio.Application.quit(self.get_application())

    #
    # 'onBackButtonPressed' is the name of the signal handler we saved in glade
    #
    @Gtk.Template.Callback()
    def onBackButtonPressed(self, widget, **_kwargs):
        assert self.back_button == widget
        # Hide the second window
        self.hide()
        # Show the first window
        self.get_application().window1.show_all()


class Application(Gtk.Application):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            application_id="clan.lol.Gtk1",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
            **kwargs,
        )
        self.window = None

    def do_activate(self):
        # Load the first window from the template
        self.window1 = AppWindow(application=self)
        # Add the first window to the application
        self.add_window(self.window1)
        # Show the first window
        self.window1.show_all()

        # Load the second window from the template
        self.window2 = SecondWindow(application=self)
        # Add the second window to the application
        self.add_window(self.window2)


def start_app(args: argparse.Namespace) -> None:
    app = Application()
    app.run()
