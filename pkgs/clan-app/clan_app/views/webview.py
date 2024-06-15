import dataclasses
import json
import logging
import sys
import threading
from collections.abc import Callable
from dataclasses import fields, is_dataclass
from pathlib import Path
from threading import Lock
from types import UnionType
from typing import Any, get_args

import gi
from clan_cli.api import API
from clan_cli.api.directory import FileRequest

gi.require_version("WebKit", "6.0")

from gi.repository import Gio, GLib, Gtk, WebKit

site_index: Path = (
    Path(sys.argv[0]).absolute() / Path("../..") / Path("clan_app/.webui/index.html")
).resolve()

log = logging.getLogger(__name__)


def dataclass_to_dict(obj: Any) -> Any:
    """
    Utility function to convert dataclasses to dictionaries
    It converts all nested dataclasses, lists, tuples, and dictionaries to dictionaries

    It does NOT convert member functions.
    """
    if dataclasses.is_dataclass(obj):
        return {k: dataclass_to_dict(v) for k, v in dataclasses.asdict(obj).items()}
    elif isinstance(obj, list | tuple):
        return [dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: dataclass_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, Path):
        return str(obj)
    else:
        return obj


# Implement the abstract open_file function
def open_file(file_request: FileRequest) -> str | None:
    # Function to handle the response and stop the loop
    selected_path = None

    def on_file_select(
        file_dialog: Gtk.FileDialog, task: Gio.Task, main_loop: GLib.MainLoop
    ) -> None:
        try:
            gfile = file_dialog.open_finish(task)
            if gfile:
                nonlocal selected_path
                selected_path = gfile.get_path()
        except Exception as e:
            print(f"Error getting selected file or directory: {e}")
        finally:
            main_loop.quit()

    def on_folder_select(
        file_dialog: Gtk.FileDialog, task: Gio.Task, main_loop: GLib.MainLoop
    ) -> None:
        try:
            gfile = file_dialog.select_folder_finish(task)
            if gfile:
                nonlocal selected_path
                selected_path = gfile.get_path()
        except Exception as e:
            print(f"Error getting selected directory: {e}")
        finally:
            main_loop.quit()

    def on_save_finish(
        file_dialog: Gtk.FileDialog, task: Gio.Task, main_loop: GLib.MainLoop
    ) -> None:
        try:
            gfile = file_dialog.save_finish(task)
            if gfile:
                nonlocal selected_path
                selected_path = gfile.get_path()
        except Exception as e:
            print(f"Error getting selected file: {e}")
        finally:
            main_loop.quit()

    dialog = Gtk.FileDialog()

    if file_request.title:
        dialog.set_title(file_request.title)

    if file_request.filters:
        filters = Gio.ListStore.new(Gtk.FileFilter)
        file_filters = Gtk.FileFilter()

        if file_request.filters.title:
            file_filters.set_name(file_request.filters.title)

        # Create and configure a filter for image files
        if file_request.filters.mime_types:
            for mime in file_request.filters.mime_types:
                file_filters.add_mime_type(mime)
                filters.append(file_filters)

        if file_request.filters.patterns:
            for pattern in file_request.filters.patterns:
                file_filters.add_pattern(pattern)

        if file_request.filters.suffixes:
            for suffix in file_request.filters.suffixes:
                file_filters.add_suffix(suffix)

        filters.append(file_filters)
        dialog.set_filters(filters)

    main_loop = GLib.MainLoop()

    # if select_folder
    if file_request.mode == "select_folder":
        dialog.select_folder(
            callback=lambda dialog, task: on_folder_select(dialog, task, main_loop),
        )
    elif file_request.mode == "open_file":
        dialog.open(
            callback=lambda dialog, task: on_file_select(dialog, task, main_loop)
        )
    elif file_request.mode == "save":
        dialog.save(
            callback=lambda dialog, task: on_save_finish(dialog, task, main_loop)
        )

    # Wait for the user to select a file or directory
    main_loop.run()  # type: ignore

    return selected_path


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
    def __init__(self, methods: dict[str, Callable]) -> None:
        self.method_registry: dict[str, Callable] = methods

        self.webview = WebKit.WebView()

        settings = self.webview.get_settings()
        # settings.
        settings.set_property("enable-developer-extras", True)
        self.webview.set_settings(settings)

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
        self,
        handler_fn: Callable[
            ...,
            Any,
        ],
        data: dict[str, Any] | None,
        method_name: str,
    ) -> None:
        with self.mutex_lock:
            log.debug("Executing... ", method_name)
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
