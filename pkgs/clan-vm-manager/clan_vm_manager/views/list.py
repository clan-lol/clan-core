from functools import partial

import gi

gi.require_version("Adw", "1")
from gi.repository import Adw, Gdk, Gtk

from clan_vm_manager.models.use_vms import VM, VMS


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

        boxed_list = Gtk.ListBox()
        boxed_list.set_selection_mode(Gtk.SelectionMode.NONE)
        boxed_list.add_css_class("boxed-list")

        def create_widget(item: VM) -> Gtk.Widget:
            flake = item.data.flake
            row = Adw.ActionRow()

            print("Creating", item.data.flake.flake_attr)
            # Title
            row.set_title(flake.clan_name)
            row.set_title_lines(1)
            row.set_title_selectable(True)

            # Subtitle
            row.set_subtitle(flake.flake_attr)
            row.set_subtitle_lines(1)

            # Avatar
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

            switch.connect("notify::active", partial(self.on_row_toggle, item))
            row.add_suffix(box)

            return row

        vms = VMS.use()

        # TODO: Move this up to create_widget and connect every VM signal to its corresponding switch
        vms.handle_vm_stopped(self.stopped_vm)
        vms.handle_vm_started(self.started_vm)

        boxed_list.bind_model(vms.list_store, create_widget_func=create_widget)

        self.append(boxed_list)

    def started_vm(self, vm: VM, _vm: VM) -> None:
        print("VM started", vm.data.flake.flake_attr)

    def stopped_vm(self, vm: VM, _vm: VM) -> None:
        print("VM stopped", vm.data.flake.flake_attr)

    def show_error_dialog(self, error: str) -> None:
        dialog = Gtk.MessageDialog(
            parent=self.get_toplevel(),
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=error,
        )
        dialog.run()
        dialog.destroy()

    def on_row_toggle(self, vm: VM, row: Adw.SwitchRow, state: bool) -> None:
        print("Toggled", vm.data.flake.flake_attr, "active:", row.get_active())

        if row.get_active():
            vm.start_async()

        if not row.get_active():
            vm.stop_async()
