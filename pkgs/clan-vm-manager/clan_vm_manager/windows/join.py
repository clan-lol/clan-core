from collections.abc import Callable
from typing import Any
from clan_cli.errors import ClanError

import gi
from clan_cli.clan_uri import ClanURI
from clan_cli.history.add import add_history, list_history

from clan_vm_manager import assets
from clan_vm_manager.errors.show_error import show_error_dialog

from ..interfaces import Callbacks, InitialJoinValues

gi.require_version("Gtk", "3.0")

from gi.repository import GdkPixbuf, Gio, Gtk


class Trust(Gtk.Box):
    def __init__(
        self,
        initial_values: InitialJoinValues,
        show_next: Callable[[], None],
        stack: Gtk.Stack,
    ) -> None:
        super().__init__()
        self.show_next = show_next
        self.stack = stack
        self.url: ClanURI | None = initial_values.url

        icon = Gtk.Image.new_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=str(assets.loc / "placeholder.jpeg"),
                width=256,
                height=256,
                preserve_aspect_ratio=True,
            )
        )
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, expand=True)
        layout.set_border_width(20)

        upper = Gtk.Box(orientation="vertical")
        upper.set_spacing(20)

        if self.url is not None:
            self.entry = Gtk.Label(label=str(self.url))
            upper.add(Gtk.Label(label="Clan URL"))
        else:
            upper.add(Gtk.Label(label="Enter Clan URL"))
            self.entry = Gtk.Entry()
            # Autocomplete
            # TODO: provide intelligent suggestions
            completion_list = Gtk.ListStore(str)
            completion_list.append(["clan://"])
            completion = Gtk.EntryCompletion()
            completion.set_model(completion_list)
            completion.set_text_column(0)
            completion.set_popup_completion(False)
            completion.set_inline_completion(True)

            self.entry.set_completion(completion)
            self.entry.set_placeholder_text("clan://")

        upper.add(icon)
        upper.add(self.entry)

        lower = Gtk.Box(orientation="vertical")
        lower.set_spacing(20)
        trust_button = Gtk.Button(label="Trust")
        trust_button.connect("clicked", self.on_trust)
        lower.add(trust_button)

        layout.pack_start(upper, expand=True, fill=True, padding=0)
        layout.pack_end(lower, expand=True, fill=True, padding=0)
        self.set_center_widget(layout)

    def on_trust(self, widget: Gtk.Widget) -> None:
        try:
            uri = self.url or ClanURI(self.entry.get_text())
            print(f"trusted: {uri}")
            add_history(uri)
            history = list_history()
            found = filter(lambda item: item.flake.flake_url == uri.get_internal(), history)
            if found:
                [item] = found
                self.stack.add_titled(
                    Details(url=uri.get_internal(), description=item.flake.description),
                    "details",
                    "Details",
                )
                self.show_next()
                self.stack.set_visible_child_name("details")

        except ClanError as e:
            show_error_dialog(e)



class Details(Gtk.Box):
    def __init__(self, url: str, description: str | None) -> None:
        super().__init__()

        icon = Gtk.Image.new_from_pixbuf(
            GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=str(assets.loc / "placeholder.jpeg"),
                width=256,
                height=256,
                preserve_aspect_ratio=True,
            )
        )
        layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, expand=True)
        layout.set_border_width(20)

        upper = Gtk.Box(orientation="vertical")
        upper.set_spacing(20)
        upper.add(Gtk.Label(label="Clan URL"))
        upper.add(icon)

        label = Gtk.Label(label=str(url))

        upper.add(label)

        description_label = Gtk.Label(label=description)
        upper.add(description_label)

        lower = Gtk.Box(orientation="horizontal", expand=True)
        lower.set_spacing(20)

        join_button = Gtk.Button(label="Join")
        join_button.connect("clicked", self.on_join)
        join_action_area = Gtk.Box(orientation="horizontal", expand=False)
        join_button_area = Gtk.Box(orientation="vertical", expand=False)
        join_action_area.pack_end(join_button_area, expand=False, fill=False, padding=0)
        join_button_area.pack_end(join_button, expand=False, fill=False, padding=0)
        join_details = Gtk.Label(label="Info")

        join_details_area = Gtk.Box(orientation="horizontal", expand=False)
        join_label_area = Gtk.Box(orientation="vertical", expand=False)
        join_label_area.pack_end(join_details, expand=False, fill=False, padding=0)
        for info in [
            "Memory: 2 GiB",
            "CPU: 2 Cores",
            "Storage: 64 GiB",
        ]:
            details_label = Gtk.Label(label=info)
            details_label.set_justify(Gtk.Justification.LEFT)
            join_label_area.pack_end(details_label, expand=False, fill=False, padding=0)

        join_details_area.pack_start(
            join_label_area, expand=False, fill=False, padding=0
        )

        lower.pack_start(join_details_area, expand=True, fill=True, padding=0)
        lower.pack_end(join_action_area, expand=True, fill=True, padding=0)
        layout.pack_start(upper, expand=False, fill=False, padding=0)
        layout.add(lower)

        self.add(layout)

    def on_join(self, widget: Gtk.Widget) -> None:
        # TODO: @Qubasa
        show_error_dialog(ClanError("Feature not ready yet."), "Info")


class JoinWindow(Gtk.ApplicationWindow):
    def __init__(self, initial_values: InitialJoinValues, cbs: Callbacks) -> None:
        super().__init__()
        # Initialize the main wincbsdow
        self.cbs = cbs
        self.set_title("cLAN Manager")
        self.connect("delete-event", self.on_quit)
        self.set_default_size(800, 600)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, expand=True)
        self.add(vbox)

        button = Gtk.ToolButton()
        button.set_icon_name("go-previous")
        button.connect("clicked", self.switch)

        toolbar = Gtk.Toolbar(orientation=Gtk.Orientation.HORIZONTAL)
        toolbar.add(button)
        vbox.add(toolbar)

        self.stack = Gtk.Stack()

        print("initial_values", initial_values)
        self.stack.add_titled(
            Trust(initial_values, show_next=self.show_details, stack=self.stack),
            "trust",
            "Trust",
        )

        vbox.add(self.stack)

        # vbox.add(Gtk.Entry(text=str(initial_values.url)))

        # Must be called AFTER all components were added
        self.show_all()

    def show_details(self) -> None:
        self.show_all()

    def switch(self, widget: Gtk.Widget) -> None:
        self.cbs.show_list()

    def on_quit(self, *args: Any) -> None:
        Gio.Application.quit(self.get_application())
