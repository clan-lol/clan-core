from collections.abc import Callable

from gi.repository import GdkPixbuf, Gtk

from ..models import VMBase, list_vms


class ClanSelectPage(Gtk.Box):
    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, expand=True)

        # TODO: We should use somekind of useState hook here
        # that updates the list of VMs when the user changes something
        vms = list_vms()

        self.selected_vm: VMBase | None = None

        list_hooks = {
            "on_cell_toggled": self.on_cell_toggled,
            "on_select_row": self.on_select_row,
            "on_double_click": self.on_double_click,
        }
        self.add(ClanSelectList(vms=vms, **list_hooks))

        button_hooks = {
            "on_start_clicked": self.on_start_clicked,
            "on_stop_clicked": self.on_stop_clicked,
            "on_backup_clicked": self.on_backup_clicked,
        }
        self.add(ClanSelectButtons(**button_hooks))

    def on_start_clicked(self, widget: Gtk.Widget) -> None:
        print("Start clicked")
        self.selected_vm.run()

    def on_stop_clicked(self, widget: Gtk.Widget) -> None:
        print("Stop clicked")

    def on_backup_clicked(self, widget: Gtk.Widget) -> None:
        print("Backup clicked")

    def on_cell_toggled(self, vm: VMBase) -> None:
        print(f"on_cell_toggled:  {vm}")

    def on_select_row(self, vm: VMBase) -> None:
        print(f"on_select_row:  {vm}")
        self.selected_vm = vm

    def on_double_click(self, vm: VMBase) -> None:
        print(f"on_double_click:  {vm}")
        vm.run()


class ClanSelectButtons(Gtk.Box):
    def __init__(
        self,
        *,
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
        button = Gtk.Button(label="Edit", margin_left=10)
        button.connect("clicked", on_backup_clicked)
        self.add(button)


class ClanSelectList(Gtk.Box):
    def __init__(
        self,
        *,
        vms: list[VMBase],
        on_cell_toggled: Callable[[VMBase, str], None],
        on_select_row: Callable[[VMBase], None],
        on_double_click: Callable[[VMBase], None],
    ) -> None:
        super().__init__(expand=True)
        self.vms = vms
        self.on_cell_toggled = on_cell_toggled
        self.on_select_row = on_select_row
        self.on_double_click = on_double_click
        store_types = VMBase.name_to_type_map().values()

        self.list_store = Gtk.ListStore(*store_types)
        for vm in vms:
            items = list(vm.list_data().values())
            items[0] = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=items[0], width=64, height=64, preserve_aspect_ratio=True
            )

            self.list_store.append(items)

        self.tree_view = Gtk.TreeView(self.list_store, expand=True)
        for idx, (key, value) in enumerate(vm.list_data().items()):
            if key.startswith("_"):
                continue
            match key:
                case "Icon":
                    renderer = Gtk.CellRendererPixbuf()
                    col = Gtk.TreeViewColumn(key, renderer, pixbuf=idx)
                    # col.add_attribute(renderer, "pixbuf", idx)
                    col.set_resizable(True)
                    col.set_expand(True)
                    col.set_property("sizing", Gtk.TreeViewColumnSizing.AUTOSIZE)
                    col.set_property("alignment", 0.5)
                    col.set_sort_column_id(idx)
                    self.tree_view.append_column(col)
                case "Name" | "URL":
                    renderer = Gtk.CellRendererText()
                    # renderer.set_property("xalign", 0.5)
                    col = Gtk.TreeViewColumn(key, renderer, text=idx)
                    col.set_resizable(True)
                    col.set_expand(True)
                    col.set_property("sizing", Gtk.TreeViewColumnSizing.AUTOSIZE)
                    col.set_property("alignment", 0.5)
                    col.set_sort_column_id(idx)
                    self.tree_view.append_column(col)
                case "Running":
                    renderer = Gtk.CellRendererToggle()
                    renderer.set_property("activatable", True)
                    renderer.connect("toggled", self._on_cell_toggled)
                    col = Gtk.TreeViewColumn(key, renderer, active=idx)
                    col.set_resizable(True)
                    col.set_expand(True)
                    col.set_property("sizing", Gtk.TreeViewColumnSizing.AUTOSIZE)
                    col.set_property("alignment", 0.5)
                    col.set_sort_column_id(idx)
                    self.tree_view.append_column(col)

        selection = self.tree_view.get_selection()
        selection.connect("changed", self._on_select_row)
        self.tree_view.connect("row-activated", self._on_double_click)

        self.set_border_width(10)
        self.add(self.tree_view)

    def _on_select_row(self, selection: Gtk.TreeSelection) -> None:
        model, row = selection.get_selected()
        if row is not None:
            print(f"Selected {model[row][1]}")
            self.on_select_row(VMBase(*model[row]))

    def _on_double_click(
        self, tree_view: Gtk.TreeView, path: Gtk.TreePath, column: Gtk.TreeViewColumn
    ) -> None:
        # Get the selection object of the tree view
        selection = tree_view.get_selection()
        model, row = selection.get_selected()
        if row is not None:
            self.on_double_click(VMBase(*model[row]))

    def _on_cell_toggled(self, widget: Gtk.CellRendererToggle, path: str) -> None:
        row = self.list_store[path]
        vm = VMBase(*row)
        self.on_cell_toggled(vm)
