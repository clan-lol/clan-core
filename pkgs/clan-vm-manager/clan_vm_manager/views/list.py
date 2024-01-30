from collections.abc import Callable
from functools import partial

import gi
from clan_cli.history.add import HistoryEntry

from clan_vm_manager.models.use_join import Join, JoinValue
from clan_vm_manager.models.use_views import Views

gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gio, GObject, Gtk

from clan_vm_manager.models.use_vms import VM, VMS


def create_boxed_list(
    model: Gio.ListStore, render_row: Callable[[Gtk.ListBox, GObject], Gtk.Widget]
) -> Gtk.ListBox:
    boxed_list = Gtk.ListBox()
    boxed_list.set_selection_mode(Gtk.SelectionMode.NONE)
    boxed_list.add_css_class("boxed-list")
    boxed_list.add_css_class("no-shadow")

    boxed_list.bind_model(model, create_widget_func=partial(render_row, boxed_list))
    return boxed_list


class ClanList(Gtk.Box):
    """
    The ClanList
    Is the composition of
    the ClanListToolbar
    the clanListView
    # ------------------------        #
    # - Tools <Start> <Stop> < Edit>  #
    # ------------------------        #
    # - List Items
    # - <...>
    # ------------------------#
    """

    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        vms = VMS.use()
        join = Join.use()

        self.join_boxed_list = create_boxed_list(
            model=join.list_store, render_row=self.render_join_row
        )

        self.vm_boxed_list = create_boxed_list(
            model=vms.list_store, render_row=self.render_vm_row
        )
        self.vm_boxed_list.add_css_class("vm-list")

        search_bar = Gtk.SearchBar()
        # This widget will typically be the top-level window
        search_bar.set_key_capture_widget(Views.use().main_window)
        entry = Gtk.SearchEntry()
        entry.set_placeholder_text("Search cLan")
        entry.connect("search-changed", self.on_search_changed)
        entry.add_css_class("search-entry")
        search_bar.set_child(entry)

        self.append(search_bar)
        self.append(self.join_boxed_list)
        self.append(self.vm_boxed_list)

    def on_search_changed(self, entry: Gtk.SearchEntry) -> None:
        VMS.use().filter_by_name(entry.get_text())
        # Disable the shadow if the list is empty
        if not VMS.use().list_store.get_n_items():
            self.vm_boxed_list.add_css_class("no-shadow")

    def render_vm_row(self, boxed_list: Gtk.ListBox, vm: VM) -> Gtk.Widget:
        if boxed_list.has_css_class("no-shadow"):
            boxed_list.remove_css_class("no-shadow")
        flake = vm.data.flake
        row = Adw.ActionRow()

        # Title
        row.set_title(flake.clan_name)

        row.set_title_lines(1)
        row.set_title_selectable(True)

        # Subtitle
        row.set_subtitle(vm.get_id())
        row.set_subtitle_lines(1)

        # # Avatar
        avatar = Adw.Avatar()
        avatar.set_custom_image(Gdk.Texture.new_from_filename(flake.icon))
        avatar.set_text(flake.clan_name + " " + flake.flake_attr)
        avatar.set_show_initials(True)
        avatar.set_size(50)
        row.add_prefix(avatar)

        # Switch
        switch = Gtk.Switch()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_valign(Gtk.Align.CENTER)
        box.append(switch)

        switch.connect("notify::active", partial(self.on_row_toggle, vm))
        vm.connect("vm_status_changed", partial(self.vm_status_changed, switch))
        row.add_suffix(box)

        return row

    def render_join_row(self, boxed_list: Gtk.ListBox, item: JoinValue) -> Gtk.Widget:
        if boxed_list.has_css_class("no-shadow"):
            boxed_list.remove_css_class("no-shadow")

        row = Adw.ActionRow()

        row.set_title(item.url.get_internal())
        row.add_css_class("trust")

        # TODO: figure out how to detect that
        if True:
            row.set_subtitle("Clan already exists. Joining again will update it")

        avatar = Adw.Avatar()
        avatar.set_text(str(item.url))
        avatar.set_show_initials(True)
        avatar.set_size(50)
        row.add_prefix(avatar)

        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.add_css_class("error")
        cancel_button.connect("clicked", partial(self.on_discard_clicked, item))

        trust_button = Gtk.Button(label="Join")
        trust_button.add_css_class("success")
        trust_button.connect("clicked", partial(self.on_trust_clicked, item))

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        box.set_valign(Gtk.Align.CENTER)
        box.append(cancel_button)
        box.append(trust_button)

        row.add_suffix(box)

        return row

    def show_error_dialog(self, error: str) -> None:
        p = Views.use().main_window

        # app = Gio.Application.get_default()
        # p = Gtk.Application.get_active_window(app)

        dialog = Adw.MessageDialog(heading="Error")
        dialog.add_response("ok", "ok")
        dialog.set_body(error)
        dialog.set_transient_for(p)  # set the parent window of the dialog
        dialog.choose()

    def on_trust_clicked(self, item: JoinValue, widget: Gtk.Widget) -> None:
        def on_join(_history: list[HistoryEntry]) -> None:
            VMS.use().refresh()

        # TODO(@hsjobeki): Confirm and edit details
        # Views.use().view.set_visible_child_name("details")

        Join.use().join(item, cb=on_join)

        # If the join request list is empty disable the shadow artefact
        if not Join.use().list_store.get_n_items():
            self.join_boxed_list.add_css_class("no-shadow")

    def on_discard_clicked(self, item: JoinValue, widget: Gtk.Widget) -> None:
        Join.use().discard(item)
        if not Join.use().list_store.get_n_items():
            self.join_boxed_list.add_css_class("no-shadow")

    def on_row_toggle(self, vm: VM, row: Adw.SwitchRow, state: bool) -> None:
        print("Toggled", vm.data.flake.flake_attr, "active:", row.get_active())

        if row.get_active():
            row.set_state(False)
            vm.start()

        if not row.get_active():
            row.set_state(True)
            vm.stop()

    def vm_status_changed(self, switch: Gtk.Switch, vm: VM, _vm: VM) -> None:
        switch.set_active(vm.is_running())
        switch.set_state(vm.is_running())
        exitc = vm.process.proc.exitcode
        print("VM exited with code:", exitc)
        if not vm.is_running() and exitc != 0:
            print("VM exited with error. Exitcode:", exitc)
            print(vm.read_log())
            # self.show_error_dialog(vm.read_log())
