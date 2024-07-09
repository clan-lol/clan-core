import dataclasses
import json
import gi
import logging
import threading
from collections.abc import Callable
from dataclasses import fields, is_dataclass
from pathlib import Path
from threading import Lock
from types import UnionType
from typing import Any, get_args

from clan_cli.api import API
from clan_app.api.file import open_file

gi.require_version("WebKit", "6.0")
from gi.repository import Gio, GLib, Gtk, WebKit

log = logging.getLogger(__name__)


def sanitize_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def dataclass_to_dict(obj: Any) -> Any:
    """
    Utility function to convert dataclasses to dictionaries
    It converts all nested dataclasses, lists, tuples, and dictionaries to dictionaries

    It does NOT convert member functions.
    """
    if dataclasses.is_dataclass(obj):
        return {
            sanitize_string(k): dataclass_to_dict(v)
            for k, v in dataclasses.asdict(obj).items()
        }
    elif isinstance(obj, list | tuple):
        return [dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {sanitize_string(k): dataclass_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, Path):
        return str(obj)
    elif isinstance(obj, str):
        return sanitize_string(obj)
    else:
        return obj



def is_union_type(type_hint: type) -> bool:
    return type(type_hint) is UnionType


def get_inner_type(type_hint: type) -> type:
    if is_union_type(type_hint):
        # Return the first non-None type
        return next(t for t in get_args(type_hint) if t is not type(None))
    return type_hint


def from_dict(t: type, data: dict[str, Any] | None) -> Any:
    """
    Dynamically instantiate a data class from a dictionary, handling nested data classes.
    """
    if not data:
        return None

    try:
        # Attempt to create an instance of the data_class
        field_values = {}
        for field in fields(t):
            field_value = data.get(field.name)
            field_type = get_inner_type(field.type)
            if field_value is not None:
                # If the field is another dataclass, recursively instantiate it
                if is_dataclass(field_type):
                    field_value = from_dict(field_type, field_value)
                elif isinstance(field_type, Path | str) and isinstance(
                    field_value, str
                ):
                    field_value = (
                        Path(field_value) if field_type == Path else field_value
                    )

            if (
                field.default is not dataclasses.MISSING
                or field.default_factory is not dataclasses.MISSING
            ):
                # Field has a default value. We cannot set the value to None
                if field_value is not None:
                    field_values[field.name] = field_value
            else:
                field_values[field.name] = field_value

        return t(**field_values)

    except (TypeError, ValueError) as e:
        print(f"Failed to instantiate {t.__name__}: {e}")
        return None


class WebView:
    def __init__(self, content_uri: str, methods: dict[str, Callable]) -> None:
        self.method_registry: dict[str, Callable] = methods

        self.webview = WebKit.WebView()

        settings = self.webview.get_settings()
        # settings.
        settings.set_property("enable-developer-extras", True)
        self.webview.set_settings(settings)
        # Fixme. This filtering is incomplete, it only triggers if a user clicks a link
        self.webview.connect("decide-policy", self.on_decide_policy)

        self.manager = self.webview.get_user_content_manager()
        # Can be called with: window.webkit.messageHandlers.gtk.postMessage("...")
        # Important: it seems postMessage must be given some payload, otherwise it won't trigger the event
        self.manager.register_script_message_handler("gtk")
        self.manager.connect("script-message-received", self.on_message_received)

        self.webview.load_uri(content_uri)
        self.content_uri = content_uri

        # global mutex lock to ensure functions run sequentially
        self.mutex_lock = Lock()
        self.queue_size = 0

    def on_decide_policy(
        self,
        webview: WebKit.WebView,
        decision: WebKit.PolicyDecision,
        decision_type: WebKit.PolicyDecisionType,
    ) -> bool:
        if decision_type != WebKit.PolicyDecisionType.NAVIGATION_ACTION:
            return False  # Continue with the default handler

        navigation_action = decision.get_navigation_action()
        request = navigation_action.get_request()
        uri = request.get_uri()
        if self.content_uri.startswith("http://") and uri.startswith(self.content_uri):
            log.debug(f"Allow navigation request: {uri}")
            return False
        elif self.content_uri.startswith("file://") and uri.startswith(
            self.content_uri
        ):
            log.debug(f"Allow navigation request: {uri}")
            return False
        log.warning(
            f"Do not allow navigation request: {uri}. Current content uri: {self.content_uri}"
        )
        decision.ignore()
        return True  # Stop other handlers from being invoked

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
        self,
        handler_fn: Callable[
            ...,
            Any,
        ],
        data: dict[str, Any] | None,
        method_name: str,
    ) -> None:
        with self.mutex_lock:
            log.debug(f"Executing... {method_name}")
            log.debug(f"{data}")
            if data is None:
                result = handler_fn()
            else:
                reconciled_arguments = {}
                op_key = data.pop("op_key", None)
                for k, v in data.items():
                    # Some functions expect to be called with dataclass instances
                    # But the js api returns dictionaries.
                    # Introspect the function and create the expected dataclass from dict dynamically
                    # Depending on the introspected argument_type
                    arg_class = API.get_method_argtype(method_name, k)
                    if dataclasses.is_dataclass(arg_class):
                        reconciled_arguments[k] = from_dict(arg_class, v)
                    else:
                        reconciled_arguments[k] = v

                r = handler_fn(**reconciled_arguments)
                # Parse the result to a serializable dictionary
                # Echo back the "op_key" to the js api
                result = dataclass_to_dict(r)
                result["op_key"] = op_key

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
