from functools import partial

import gi
from clan_cli.clan_uri import ClanURI
from clan_cli.errors import ClanError
from clan_cli.history.add import add_history

from clan_vm_manager.errors.show_error import show_error_dialog

from ..interfaces import InitialJoinValues

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")


from gi.repository import Adw, Gio, GObject, Gtk


class TrustValues(GObject.Object):
    data: InitialJoinValues

    def __init__(self, data: InitialJoinValues) -> None:
        super().__init__()
        print("TrustValues", data)
        self.data = data


class Trust(Gtk.Box):
    def __init__(
        self,
        *,
        initial_values: InitialJoinValues,
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        # self.on_trust = on_trust
        self.url: ClanURI | None = initial_values.url

        def render(item: TrustValues) -> Gtk.Widget:
            row = Adw.ActionRow()
            row.set_title(str(item.data.url))
            row.add_css_class("trust")

            avatar = Adw.Avatar()
            avatar.set_text(str(item.data.url))
            avatar.set_show_initials(True)
            avatar.set_size(50)
            row.add_prefix(avatar)

            cancel_button = Gtk.Button(label="Cancel")
            cancel_button.add_css_class("error")

            trust_button = Gtk.Button(label="Trust")
            trust_button.add_css_class("success")
            trust_button.connect("clicked", partial(self.on_trust_clicked, item.data))

            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            box.set_valign(Gtk.Align.CENTER)
            box.append(cancel_button)
            box.append(trust_button)

            # switch.connect("notify::active", partial(self.on_row_toggle, item.data))
            row.add_suffix(box)

            return row

        boxed_list = Gtk.ListBox()
        boxed_list.set_selection_mode(Gtk.SelectionMode.NONE)
        boxed_list.add_css_class("boxed-list")

        list_store = Gio.ListStore.new(TrustValues)
        list_store.append(TrustValues(data=initial_values))

        # icon = Gtk.Image.new_from_pixbuf(
        #     GdkPixbuf.Pixbuf.new_from_file_at_scale(
        #         filename=str(assets.loc / "placeholder.jpeg"),
        #         width=256,
        #         height=256,
        #         preserve_aspect_ratio=True,
        #     )
        # )

        boxed_list.bind_model(list_store, create_widget_func=render)

        self.append(boxed_list)

        # layout = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # # layout.set_border_width(20)
        # layout.set_spacing(20)

        # if self.url is not None:
        #     self.entry = Gtk.Label(label=str(self.url))
        #     layout.append(icon)
        #     layout.append(Gtk.Label(label="Clan URL"))
        # else:
        #     layout.append(Gtk.Label(label="Enter Clan URL"))
        #     self.entry = Gtk.Entry()
        #     # Autocomplete
        #     # TODO: provide intelligent suggestions
        #     completion_list = Gtk.ListStore(str)
        #     completion_list.append(["clan://"])
        #     completion = Gtk.EntryCompletion()
        #     completion.set_model(completion_list)
        #     completion.set_text_column(0)
        #     completion.set_popup_completion(False)
        #     completion.set_inline_completion(True)

        #     self.entry.set_completion(completion)
        #     self.entry.set_placeholder_text("clan://")

        # layout.append(self.entry)

        # if self.url is None:
        #     trust_button = Gtk.Button(label="Load cLAN-URL")
        # else:
        #     trust_button = Gtk.Button(label="Trust cLAN-URL")

        # trust_button.connect("clicked", self.on_trust_clicked)
        # layout.append(trust_button)

    def on_trust_clicked(self, item: InitialJoinValues, widget: Gtk.Widget) -> None:
        try:
            uri = item.url
            # or ClanURI(self.entry.get_text())
            print(f"trusted: {uri}")
            if uri:
                add_history(uri)
                # history = list_history()

                # found = filter(
                #     lambda item: item.flake.flake_url == uri.get_internal(), history
                # )
                # if found:
                # [item] = found
                # self.on_trust(uri.get_internal(), item.flake)

        except ClanError as e:
            pass
            show_error_dialog(e)
