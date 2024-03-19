import logging

import gi

gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, Gtk

from clan_vm_manager.singletons.use_views import ViewStack

log = logging.getLogger(__name__)


class Logs(Gtk.Box):
    """
    Simple log view
    This includes a banner and a text view and a button to close the log and navigate back to the overview
    """

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        app = Gio.Application.get_default()
        assert app is not None

        self.banner = Adw.Banner.new("")
        self.banner.set_use_markup(True)
        self.banner.set_revealed(True)
        self.banner.set_button_label("Close")

        self.banner.connect(
            "button-clicked",
            lambda _: ViewStack.use().view.set_visible_child_name("list"),
        )

        self.text_view = Gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_view.add_css_class("log-view")

        self.append(self.banner)
        self.append(self.text_view)

    def set_title(self, title: str) -> None:
        self.banner.set_title(title)

    def set_message(self, message: str) -> None:
        """
        Set the log message. This will delete any previous message
        """
        buffer = self.text_view.get_buffer()
        buffer.set_text(message)

        mark = buffer.create_mark(None, buffer.get_end_iter(), False)  # type: ignore
        self.text_view.scroll_to_mark(mark, 0.05, True, 0.0, 1.0)

    def append_message(self, message: str) -> None:
        """
        Append to the end of a potentially existent log message
        """
        buffer = self.text_view.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, message)  # type: ignore

        mark = buffer.create_mark(None, buffer.get_end_iter(), False)  # type: ignore
        self.text_view.scroll_to_mark(mark, 0.05, True, 0.0, 1.0)
