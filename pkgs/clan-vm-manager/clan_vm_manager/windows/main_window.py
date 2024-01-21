import gi

from clan_vm_manager.models.interfaces import ClanConfig
from clan_vm_manager.models.use_views import Views
from clan_vm_manager.views.details import Details
from clan_vm_manager.views.list import ClanList

gi.require_version("Adw", "1")

from gi.repository import Adw


class MainWindow(Adw.ApplicationWindow):
    def __init__(self, config: ClanConfig) -> None:
        super().__init__()
        self.set_title("cLAN Manager")
        self.set_default_size(980, 650)

        view = Adw.ToolbarView()
        self.set_content(view)

        header = Adw.HeaderBar()
        view.add_top_bar(header)

        # Initialize all views
        stack_view = Views.use().view
        Views.use().set_main_window(self)

        stack_view.add_named(ClanList(), "list")
        stack_view.add_named(Details(), "details")

        stack_view.set_visible_child_name(config.initial_view)

        clamp = Adw.Clamp()
        clamp.set_child(stack_view)
        clamp.set_maximum_size(1000)

        view.set_content(clamp)
