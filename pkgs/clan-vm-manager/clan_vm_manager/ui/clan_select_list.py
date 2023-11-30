from collections.abc import Callable
from typing import TYPE_CHECKING

from gi.repository import Gtk

if TYPE_CHECKING:
    from ..app import VM


class ClanSelectPage(Gtk.Box):
    def __init__(self, vms: list["VM"]) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, expand=True)

        self.add(ClanSelectList(vms, self.on_cell_toggled, self.on_select_row))
        self.add(
            ClanSelectButtons(
                self.on_start_clicked, self.on_stop_clicked, self.on_backup_clicked
            )
        )

    def on_start_clicked(self, widget: Gtk.Widget) -> None:
        print("Start clicked")

    def on_stop_clicked(self, widget: Gtk.Widget) -> None:
        print("Stop clicked")

    def on_backup_clicked(self, widget: Gtk.Widget) -> None:
        print("Backup clicked")

    def on_cell_toggled(self, widget: Gtk.Widget, path: str) -> None:
        print(f"on_cell_toggled:  {path}")
        # Get the current value from the model
        current_value = self.list_store[path][1]

        print(f"current_value: {current_value}")
        # Toggle the value
        self.list_store[path][1] = not current_value
        # Print the updated value
        print("Switched", path, "to", self.list_store[path][1])

    def on_select_row(self, selection: Gtk.TreeSelection) -> None:
        model, row = selection.get_selected()
        if row is not None:
            print(f"Selected {model[row][0]}")


class ClanSelectButtons(Gtk.Box):
    def __init__(
        self,
        on_start_clicked: Callable[[Gtk.Widget], None],
        on_stop_clicked: Callable[[Gtk.Widget], None],
        on_backup_clicked: Callable[[Gtk.Widget], None],
    ) -> None:
        super().__init__(
            orientation=Gtk.Orientation.HORIZONTAL, margin_bottom=10, margin_top=10
        )

        button = Gtk.Button(label="Start", margin_left=10)
        button.connect("clicked", on_start_clicked)
        self.add(button)
        button = Gtk.Button(label="Stop", margin_left=10)
        button.connect("clicked", on_stop_clicked)
        self.add(button)
        button = Gtk.Button(label="Backup", margin_left=10)
        button.connect("clicked", on_backup_clicked)
        self.add(button)


class ClanSelectList(Gtk.Box):
    def __init__(
        self,
        vms: list["VM"],
        on_cell_toggled: Callable[[Gtk.Widget, str], None],
        on_select_row: Callable[[Gtk.TreeSelection], None],
    ) -> None:
        super().__init__(expand=True)
        self.vms = vms

        self.list_store = Gtk.ListStore(str, bool, str)
        for vm in vms:
            items = list(vm.__dict__.values())
            print(f"Table: {items}")
            self.list_store.append(items)

        self.tree_view = Gtk.TreeView(self.list_store, expand=True)
        for idx, (key, value) in enumerate(vm.__dict__.items()):
            if isinstance(value, str):
                renderer = Gtk.CellRendererText()
                # renderer.set_property("xalign", 0.5)
                col = Gtk.TreeViewColumn(key.capitalize(), renderer, text=idx)
                col.set_resizable(True)
                col.set_expand(True)
                col.set_property("sizing", Gtk.TreeViewColumnSizing.AUTOSIZE)
                col.set_property("alignment", 0.5)
                col.set_sort_column_id(idx)
                self.tree_view.append_column(col)
            if isinstance(value, bool):
                renderer = Gtk.CellRendererToggle()
                renderer.set_property("activatable", True)
                renderer.connect("toggled", on_cell_toggled)
                col = Gtk.TreeViewColumn(key.capitalize(), renderer, active=idx)
                col.set_resizable(True)
                col.set_expand(True)
                col.set_property("sizing", Gtk.TreeViewColumnSizing.AUTOSIZE)
                col.set_property("alignment", 0.5)
                col.set_sort_column_id(idx)
                self.tree_view.append_column(col)

        selection = self.tree_view.get_selection()
        selection.connect("changed", on_select_row)

        self.set_border_width(10)
        self.add(self.tree_view)
