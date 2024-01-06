import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

from ..models import VMBase


class VmMenu(Gtk.Menu):
    def __init__(self, vm: VMBase) -> None:
        super().__init__()
        self.vm = vm
        self.menu_items = [
            ("Start", self.start_vm),
            ("Stop", self.stop_vm),
            ("Edit", self.edit_vm),
            ("Remove", self.remove_vm),
            ("Write to USB", self.write_to_usb),
        ]
        for item in self.menu_items:
            menu_item = Gtk.MenuItem(label=item[0])
            menu_item.connect("activate", item[1])
            self.append(menu_item)
        # self.show_all()

    def start_vm(self, widget: Gtk.Widget) -> None:
        print("start_vm")

    def stop_vm(self, widget: Gtk.Widget) -> None:
        print("stop_vm")

    def edit_vm(self, widget: Gtk.Widget) -> None:
        print("edit_vm")

    def remove_vm(self, widget: Gtk.Widget) -> None:
        print("remove_vm")

    def write_to_usb(self, widget: Gtk.Widget) -> None:
        print("write_to_usb")
