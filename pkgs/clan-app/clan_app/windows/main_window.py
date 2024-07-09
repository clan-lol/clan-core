import logging
import threading

import gi
from clan_cli.api import API
from clan_cli.history.list import list_history

from clan_app.components.interfaces import ClanConfig
from clan_app.singletons.toast import ToastOverlay
from clan_app.singletons.use_views import ViewStack


from clan_app.views.webview import WebView, open_file

gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, GLib


log = logging.getLogger(__name__)


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, config: ClanConfig) -> None:
        super().__init__()
        self.set_title("Clan Manager")
        self.set_default_size(980, 850)

        # Overlay for GTK side exclusive toasts
        overlay = ToastOverlay.use().overlay
        view = Adw.ToolbarView()
        overlay.set_child(view)

        self.set_content(overlay)

        header = Adw.HeaderBar()
        view.add_top_bar(header)

        app = Gio.Application.get_default()
        assert app is not None

        stack_view = ViewStack.use().view

        # Override platform specific functions
        API.register(open_file)

        webview = WebView(methods=API._registry, content_uri=config.content_uri)

        stack_view.add_named(webview.get_webview(), "webview")
        stack_view.set_visible_child_name(config.initial_view)

        view.set_content(stack_view)

        self.connect("destroy", self.on_destroy)

    def on_destroy(self, source: "Adw.ApplicationWindow") -> None:
        log.debug("====Destroying Adw.ApplicationWindow===")

