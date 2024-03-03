import logging
import threading
from typing import Any

import gi
from clan_cli.history.list import list_history

from clan_vm_manager.components.interfaces import ClanConfig
from clan_vm_manager.singletons.use_views import ViewStack
from clan_vm_manager.singletons.use_vms import ClanStore
from clan_vm_manager.views.details import Details
from clan_vm_manager.views.list import ClanList

gi.require_version("Adw", "1")

from gi.repository import Adw, Gio, GLib, Gtk

from clan_vm_manager.components.trayicon import TrayIcon

log = logging.getLogger(__name__)


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, config: ClanConfig) -> None:
        super().__init__()
        self.set_title("cLAN Manager")
        self.set_default_size(980, 650)

        view = Adw.ToolbarView()
        self.set_content(view)

        header = Adw.HeaderBar()
        view.add_top_bar(header)

        app = Gio.Application.get_default()
        self.tray_icon: TrayIcon = TrayIcon(app)

        # Initialize all ClanStore
        threading.Thread(target=self._populate_vms).start()

        # Initialize all views
        stack_view = ViewStack.use().view

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

    def _populate_vms(self) -> None:
        # Execute `clan flakes add <path>` to democlan for this to work
        # TODO: Make list_history a generator function
        for entry in list_history():
            GLib.idle_add(ClanStore.use().create_vm_task, entry)

    def on_destroy(self, *_args: Any) -> None:
        self.tray_icon.destroy()
        ClanStore.use().kill_all()
