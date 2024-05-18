import dataclasses
import json
import sys
import threading
from collections.abc import Callable
from pathlib import Path
from typing import Any, Union

import gi
from clan_cli import machines

gi.require_version("WebKit", "6.0")

from gi.repository import GLib, WebKit

site_index: Path = (
    Path(sys.argv[0]).absolute()
    / Path("../..")
    / Path("clan_vm_manager/.webui/index.html")
).resolve()


def type_to_dict(t: Any) -> dict:
    if dataclasses.is_dataclass(t):
        fields = dataclasses.fields(t)
        return {
            "type": "dataclass",
            "name": t.__name__,
            "fields": {f.name: type_to_dict(f.type) for f in fields},
        }

    if hasattr(t, "__origin__"):  # Check if it's a generic type
        if t.__origin__ is None:
            # Non-generic user-defined or built-in type
            return {"type": t.__name__}
        if t.__origin__ is Union:
            return {"type": "union", "of": [type_to_dict(arg) for arg in t.__args__]}
        elif issubclass(t.__origin__, list):
            return {"type": "list", "item_type": type_to_dict(t.__args__[0])}
        elif issubclass(t.__origin__, dict):
            return {
                "type": "dict",
                "key_type": type_to_dict(t.__args__[0]),
                "value_type": type_to_dict(t.__args__[1]),
            }
        elif issubclass(t.__origin__, tuple):
            return {
                "type": "tuple",
                "element_types": [type_to_dict(elem) for elem in t.__args__],
            }
        elif issubclass(t.__origin__, set):
            return {"type": "set", "item_type": type_to_dict(t.__args__[0])}
        else:
            # Handle other generic types (like Union, Optional)
            return {
                "type": str(t.__origin__.__name__),
                "parameters": [type_to_dict(arg) for arg in t.__args__],
            }
    elif isinstance(t, type):
        return {"type": t.__name__}
    else:
        return {"type": str(t)}


class WebView:
    def __init__(self) -> None:
        self.method_registry: dict[str, Callable] = {}

        self.webview = WebKit.WebView()
        self.manager = self.webview.get_user_content_manager()
        # Can be called with: window.webkit.messageHandlers.gtk.postMessage("...")
        # Important: it seems postMessage must be given some payload, otherwise it won't trigger the event
        self.manager.register_script_message_handler("gtk")
        self.manager.connect("script-message-received", self.on_message_received)

        self.webview.load_uri(f"file://{site_index}")

    def method(self, function: Callable) -> Callable:
        # type_hints = get_type_hints(function)
        # serialized_hints = {key: type_to_dict(value) for key, value in type_hints.items()}
        self.method_registry[function.__name__] = function
        return function

    def on_message_received(
        self, user_content_manager: WebKit.UserContentManager, message: Any
    ) -> None:
        payload = json.loads(message.to_json(0))
        print(f"Received message: {payload}")
        method_name = payload["method"]
        handler_fn = self.method_registry[method_name]

        # Start handler_fn in a new thread
        thread = threading.Thread(
            target=self.threaded_handler,
            args=(handler_fn, payload.get("data"), method_name),
        )
        thread.start()

    def threaded_handler(
        self, handler_fn: Callable[[Any], Any], data: Any, method_name: str
    ) -> None:
        result = handler_fn(data)
        serialized = json.dumps(result)

        # Use idle_add to queue the response call to js on the main GTK thread
        GLib.idle_add(self.call_js, method_name, serialized)

    def call_js(self, method_name: str, serialized: str) -> bool:
        # This function must be run on the main GTK thread to interact with the webview
        self.webview.evaluate_javascript(
            f"""
            window.clan.{method_name}(`{serialized}`);
            """,
            -1,
            None,
            None,
            None,
        )
        return False  # Important to return False so that it's not run again

    def get_webview(self) -> WebKit.WebView:
        return self.webview


webview = WebView()


@webview.method
def list_machines(data: None) -> list[str]:
    return machines.list.list_machines(".")
