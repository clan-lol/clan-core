from typing import Any

import gi

from clan_vm_manager.models.interfaces import ClanConfig
from clan_vm_manager.models.use_views import Views
from clan_vm_manager.models.use_vms import VMs
from clan_vm_manager.views.details import Details
from clan_vm_manager.views.list import ClanList

gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, Gtk

from ..trayicon import TrayIcon


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, config: ClanConfig) -> None:
        super().__init__()
        self.set_title("cLAN Manager")
        self.set_default_size(980, 650)

        view = Adw.ToolbarView()
        self.set_content(view)

        header = Adw.HeaderBar()
        view.add_top_bar(header)

        self.vms = VMs.use()
        app = Gio.Application.get_default()
        self.tray_icon: TrayIcon = TrayIcon(app)

        # Initialize all views
        stack_view = Views.use().view
        Views.use().set_main_window(self)

        scroll = Gtk.ScrolledWindow()
        scroll.set_propagate_natural_height(True)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_child(ClanList(config))

        stack_view.add_named(scroll, "list")
        stack_view.add_named(Details(), "details")

        stack_view.set_visible_child_name(config.initial_view)

        clamp = Adw.Clamp()
        clamp.set_child(stack_view)
        clamp.set_maximum_size(1000)

        view.set_content(clamp)

        self.connect("destroy", self.on_destroy)

    def on_destroy(self, *_args: Any) -> None:
        self.tray_icon.destroy()
        self.vms.kill_all()
