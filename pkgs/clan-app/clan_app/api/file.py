# ruff: noqa: N801
import gi

gi.require_version("Gtk", "4.0")

import logging
from pathlib import Path
from typing import Any

from clan_cli.api import ErrorDataClass, SuccessDataClass
from clan_cli.api.directory import FileRequest
from gi.repository import Gio, GLib, Gtk

from clan_app.api import ImplFunc

log = logging.getLogger(__name__)


# This implements the abstract function open_file with one argument, file_request,
# which is a FileRequest object and returns a string or None.
class open_file(
    ImplFunc[[FileRequest, str], SuccessDataClass[list[str] | None] | ErrorDataClass]
):
    def __init__(self) -> None:
        super().__init__()

    def async_run(self, file_request: FileRequest, op_key: str) -> bool:
        def on_file_select(file_dialog: Gtk.FileDialog, task: Gio.Task) -> None:
            try:
                gfile = file_dialog.open_finish(task)
                if gfile:
                    selected_path = [gfile.get_path()]
                    self.returns(
                        SuccessDataClass(
                            op_key=op_key, data=selected_path, status="success"
                        )
                    )
            except Exception as e:
                print(f"Error getting selected file or directory: {e}")

        def on_file_select_multiple(
            file_dialog: Gtk.FileDialog, task: Gio.Task
        ) -> None:
            try:
                gfiles: Any = file_dialog.open_multiple_finish(task)
                if gfiles:
                    selected_paths = [gfile.get_path() for gfile in gfiles]
                    self.returns(
                        SuccessDataClass(
                            op_key=op_key, data=selected_paths, status="success"
                        )
                    )
            except Exception as e:
                print(f"Error getting selected files: {e}")

        def on_folder_select(file_dialog: Gtk.FileDialog, task: Gio.Task) -> None:
            try:
                gfile = file_dialog.select_folder_finish(task)
                if gfile:
                    selected_path = [gfile.get_path()]
                    self.returns(
                        SuccessDataClass(
                            op_key=op_key, data=selected_path, status="success"
                        )
                    )
            except Exception as e:
                print(f"Error getting selected directory: {e}")

        def on_save_finish(file_dialog: Gtk.FileDialog, task: Gio.Task) -> None:
            try:
                gfile = file_dialog.save_finish(task)
                if gfile:
                    selected_path = [gfile.get_path()]
                    self.returns(
                        SuccessDataClass(
                            op_key=op_key, data=selected_path, status="success"
                        )
                    )
            except Exception as e:
                print(f"Error getting selected file: {e}")

        dialog = Gtk.FileDialog()

        if file_request.title:
            dialog.set_title(file_request.title)

        if file_request.filters:
            filters = Gio.ListStore.new(Gtk.FileFilter)
            file_filters = Gtk.FileFilter()

            if file_request.filters.title:
                file_filters.set_name(file_request.filters.title)

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

        if file_request.initial_file:
            p = Path(file_request.initial_file).expanduser()
            f = Gio.File.new_for_path(str(p))
            dialog.set_initial_file(f)

        if file_request.initial_folder:
            p = Path(file_request.initial_folder).expanduser()
            f = Gio.File.new_for_path(str(p))
            dialog.set_initial_folder(f)

        # if select_folder
        if file_request.mode == "select_folder":
            dialog.select_folder(callback=on_folder_select)
        if file_request.mode == "open_multiple_files":
            dialog.open_multiple(callback=on_file_select_multiple)
        elif file_request.mode == "open_file":
            dialog.open(callback=on_file_select)
        elif file_request.mode == "save":
            dialog.save(callback=on_save_finish)

        return GLib.SOURCE_REMOVE
