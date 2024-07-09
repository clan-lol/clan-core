import gi

gi.require_version("WebKit", "6.0")

from gi.repository import Gio, GLib, Gtk, WebKit


from clan_cli.api.directory import FileRequest


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
