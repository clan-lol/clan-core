import json
import logging
import sys
import threading
from collections.abc import Callable
from pathlib import Path
from threading import Lock
from typing import Any

import gi

gi.require_version("WebKit", "6.0")

from gi.repository import GLib, WebKit

site_index: Path = (
    Path(sys.argv[0]).absolute()
    / Path("../..")
    / Path("clan_vm_manager/.webui/index.html")
).resolve()

log = logging.getLogger(__name__)


class WebView:
    def __init__(self, methods: dict[str, Callable]) -> None:
        self.method_registry: dict[str, Callable] = methods

        self.webview = WebKit.WebView()
        self.manager = self.webview.get_user_content_manager()
        # Can be called with: window.webkit.messageHandlers.gtk.postMessage("...")
        # Important: it seems postMessage must be given some payload, otherwise it won't trigger the event
        self.manager.register_script_message_handler("gtk")
        self.manager.connect("script-message-received", self.on_message_received)

        self.webview.load_uri(f"file://{site_index}")

        # global mutex lock to ensure functions run sequentially
        self.mutex_lock = Lock()
        self.queue_size = 0

    def on_message_received(
        self, user_content_manager: WebKit.UserContentManager, message: Any
    ) -> None:
        payload = json.loads(message.to_json(0))
        method_name = payload["method"]
        handler_fn = self.method_registry[method_name]

        log.debug(f"Received message: {payload}")
        log.debug(f"Queue size: {self.queue_size} (Wait)")

        def threaded_wrapper() -> bool:
            """
            Ensures only one function is executed at a time

            Wait until there is no other function acquiring the global lock.

            Starts a thread with the potentially long running API function within.
            """
            if not self.mutex_lock.locked():
                thread = threading.Thread(
                    target=self.threaded_handler,
                    args=(
                        handler_fn,
                        payload.get("data"),
                        method_name,
                    ),
                )
                thread.start()
                return GLib.SOURCE_REMOVE

            return GLib.SOURCE_CONTINUE

        GLib.idle_add(
            threaded_wrapper,
        )
        self.queue_size += 1

    def threaded_handler(
        self, handler_fn: Callable[[Any], Any], data: Any, method_name: str
    ) -> None:
        with self.mutex_lock:
            log.debug("Executing... ", method_name)
            result = handler_fn(data)
            serialized = json.dumps(result)

            # Use idle_add to queue the response call to js on the main GTK thread
            GLib.idle_add(self.return_data_to_js, method_name, serialized)
        self.queue_size -= 1
        log.debug(f"Done: Remaining queue size: {self.queue_size}")

    def return_data_to_js(self, method_name: str, serialized: str) -> bool:
        # This function must be run on the main GTK thread to interact with the webview
        # result = method_fn(data) # takes very long
        # serialized = result
        self.webview.evaluate_javascript(
            f"""
            window.clan.{method_name}(`{serialized}`);
            """,
            -1,
            None,
            None,
            None,
        )
        return GLib.SOURCE_REMOVE

    def get_webview(self) -> WebKit.WebView:
        return self.webview
