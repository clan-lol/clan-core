from typing import Any

import gi

from ..models import VMBase, get_initial_vms

gi.require_version("Gtk", "4.0")

from gi.repository import Gio, Gtk

from ..interfaces import Callbacks
from ..ui.clan_join_page import ClanJoinPage
from ..ui.clan_select_list import ClanEdit, ClanList


class OverviewWindow(Gtk.ApplicationWindow):
    def __init__(self, cbs: Callbacks) -> None:
        super().__init__()
        self.set_title("cLAN Manager")
        # self.connect("delete-event", self.on_quit)
        self.set_default_size(800, 600)
        self.cbs = cbs

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, )
        self.set_child(vbox)
        self.stack = Gtk.Stack()

        clan_list = ClanList(
            vms=[vm.base for vm in get_initial_vms(self.cbs.running_vms())],
            cbs=self.cbs,
            remount_list=self.remount_list_view,
            remount_edit=self.remount_edit_view,
            set_selected=self.set_selected,
            selected_vm=None,
        )

        # Add named stacks
        self.stack.add_titled(clan_list, "list", "List")
        self.stack.add_titled(
            ClanJoinPage(stack=self.remount_list_view), "join", "Join"
        )
        self.stack.add_titled(
            ClanEdit(remount_list=self.remount_list_view, selected_vm=None),
            "edit",
            "Edit",
        )

        vbox.append(self.stack)

        # Must be called AFTER all components were added
        # self.show_all()

    def set_selected(self, sel: VMBase | None) -> None:
        self.selected_vm = sel

    def remount_list_view(self) -> None:
        widget = self.stack.get_child_by_name("list")
        if widget:
            widget.destroy()
        vms = []

        for vm in get_initial_vms(self.cbs.running_vms()):
            vms.append(vm.base)
            # FIXME: It feels very odd that we have to re-fetch the selected VM.
            #        The model should be just updated in-place.
            if self.selected_vm and vm.base.url == self.selected_vm.url:
                self.selected_vm = vm.base

        clan_list = ClanList(
            vms=vms,
            cbs=self.cbs,
            remount_list=self.remount_list_view,
            remount_edit=self.remount_edit_view,
            set_selected=self.set_selected,
            selected_vm=self.selected_vm,
        )
        self.stack.add_titled(clan_list, "list", "List")
        # self.show_all()
        self.stack.set_visible_child_name("list")

    def remount_edit_view(self) -> None:
        widget = self.stack.get_child_by_name("edit")
        if widget:
            widget.destroy()

        self.stack.add_titled(
            ClanEdit(remount_list=self.remount_list_view, selected_vm=self.selected_vm),
            "edit",
            "Edit",
        )
        # self.show_all()
        self.stack.set_visible_child_name("edit")

    def on_quit(self, *args: Any) -> None:
        Gio.Application.quit(self.get_application())
