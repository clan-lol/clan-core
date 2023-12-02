from collections.abc import Callable

from gi.repository import GdkPixbuf, Gtk

from ..models import VMBase, get_initial_vms


class ClanSelectPage(Gtk.Box):
    def __init__(self, reload: Callable[[], None]) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, expand=True)

        # TODO: We should use somekind of useState hook here.
        # that updates the list of VMs when the user changes something
        # @hsjobeki reply: @qubasa: This is how to update data in the list store
        # self.list_store.set_value(self.list_store.get_iter(path), 3, "new value")
        # self.list_store[path][3] = "new_value"
        # This class needs to take ownership of the data because it has access to the listStore only
        self.selected_vm: VMBase | None = None

        self.list_hooks = {
            "on_select_row": self.on_select_vm,
        }
        self.add(ClanSelectList(**self.list_hooks))
        self.reload = reload
        button_hooks = {
            "on_start_clicked": self.on_start_clicked,
            "on_stop_clicked": self.on_stop_clicked,
            "on_backup_clicked": self.on_backup_clicked,
        }
        self.add(ClanSelectButtons(**button_hooks))

    def on_start_clicked(self, widget: Gtk.Widget) -> None:
        print("Start clicked")
        if self.selected_vm:
            self.selected_vm.run()
        self.reload()

    def on_stop_clicked(self, widget: Gtk.Widget) -> None:
        print("Stop clicked")

    def on_backup_clicked(self, widget: Gtk.Widget) -> None:
        print("Backup clicked")

    def on_select_vm(self, vm: VMBase) -> None:
        print(f"on_select_vm: {vm}")
        self.selected_vm = vm


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
        # vms: list[VMBase],
        on_select_row: Callable[[VMBase], None],
        # on_double_click: Callable[[VMBase], None],
    ) -> None:
        super().__init__(expand=True)
        self.vms: list[VMBase] = [vm.base for vm in get_initial_vms()]
        self.on_select_row = on_select_row
        store_types = VMBase.name_to_type_map().values()

        self.list_store = Gtk.ListStore(*store_types)
        self.tree_view = Gtk.TreeView(self.list_store, expand=True)
        for vm in self.vms:
            self.insertVM(vm)

        setColRenderers(self.tree_view)

        selection = self.tree_view.get_selection()
        selection.connect("changed", self._on_select_row)
        self.tree_view.connect("row-activated", self._on_double_click)

        self.set_border_width(10)
        self.add(self.tree_view)

    def insertVM(self, vm: VMBase) -> None:
        values = list(vm.list_data().values())
        values[0] = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=values[0], width=64, height=64, preserve_aspect_ratio=True
        )
        self.list_store.append(values)

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
            VMBase(*model[row]).run()


def setColRenderers(tree_view: Gtk.TreeView) -> None:
    for idx, (key, _) in enumerate(VMBase.name_to_type_map().items()):
        col: Gtk.TreeViewColumn = None
        match key:
            case "Icon":
                renderer = Gtk.CellRendererPixbuf()
                col = Gtk.TreeViewColumn(key, renderer, pixbuf=idx)
            case "Name" | "URL":
                renderer = Gtk.CellRendererText()
                col = Gtk.TreeViewColumn(key, renderer, text=idx)
            case "Status":
                renderer = Gtk.CellRendererText()
                col = Gtk.TreeViewColumn(key, renderer, text=idx)
            case _:
                continue

        # CommonSetup for all columns
        if col:
            col.set_resizable(True)
            col.set_expand(True)
            col.set_property("sizing", Gtk.TreeViewColumnSizing.AUTOSIZE)
            col.set_property("alignment", 0.5)
            col.set_sort_column_id(idx)
            tree_view.append_column(col)
