from collections.abc import Callable

from gi.repository import GdkPixbuf, Gtk

from ..models import VMBase, get_initial_vms


class ClanEditForm(Gtk.ListBox):
    def __init__(self, selected: VMBase | None) -> None:
        super().__init__()
        self.page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, expand=True)
        self.set_border_width(10)
        self.selected = selected
        self.set_selection_mode(0)

        if self.selected:
            row = Gtk.ListBoxRow()
            row.add(Gtk.Label(f"\n {self.selected.name}"))
            self.add(row)

        # ---------- row 1 --------
        row = Gtk.ListBoxRow()
        row_layout = Gtk.Box(spacing=6, expand=True)

        # Doc: pack_start/end takes alignment params Expand, Fill, Padding
        row_layout.pack_start(Gtk.Label("Memory Size in MiB"), False, False, 5)
        row_layout.pack_start(
            Gtk.SpinButton.new_with_range(512, 4096, 256), True, True, 0
        )

        row.add(row_layout)
        self.add(row)

        # ----------- row 2 -------

        row = Gtk.ListBoxRow()
        row_layout = Gtk.Box(spacing=6, expand=True)

        row_layout.pack_start(Gtk.Label("CPU Count"), False, False, 5)
        row_layout.pack_end(Gtk.SpinButton.new_with_range(1, 5, 1), True, True, 0)

        row.add(row_layout)
        self.add(row)

    def switch(self, widget: Gtk.Widget) -> None:
        self.show_list()


class ClanEdit(Gtk.Box):
    def __init__(self, show_list: Callable[[], None], selected: VMBase | None) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, expand=True)

        self.show_list = show_list
        self.selected = selected

        button_hooks = {
            "on_save_clicked": self.on_save,
        }

        self.toolbar = ClanEditToolbar(**button_hooks)
        self.add(self.toolbar)
        self.add(ClanEditForm(self.selected))

    def on_save(self, widget: Gtk.Widget) -> None:
        print("Save clicked saving values")
        self.show_list()


class ClanList(Gtk.Box):
    """
    The ClanList
    Is the composition of
    the ClanListToolbar
    the clanListView
    # ------------------------#
    # - Tools <Join> < Edit>  #
    # ------------------------#
    # - List Items
    # - <...>
    # ------------------------#
    """

    def __init__(
        self,
        show_list: Callable[[], None],
        show_edit: Callable[[], None],
        set_selected: Callable[[VMBase | None], None],
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, expand=True)

        self.show_edit = show_edit
        self.show_list = show_list
        self.set_selected = set_selected

        # TODO: We should use somekind of useState hook here.
        # that updates the list of VMs when the user changes something
        # @hsjobeki reply: @qubasa: This is how to update data in the list store
        # self.list_store.set_value(self.list_store.get_iter(path), 3, "new value")
        # self.list_store[path][3] = "new_value"
        # This class needs to take ownership of the data because it has access to the listStore only
        self.selected_vm: VMBase | None = None

        button_hooks = {
            "on_start_clicked": self.on_start_clicked,
            "on_stop_clicked": self.on_stop_clicked,
            "on_edit_clicked": self.on_edit_clicked,
        }
        self.toolbar = ClanListToolbar(**button_hooks)
        self.toolbar.set_is_selected(False)
        self.add(self.toolbar)

        self.list_hooks = {
            "on_select_row": self.on_select_vm,
        }
        self.add(ClanListView(**self.list_hooks))

    def on_start_clicked(self, widget: Gtk.Widget) -> None:
        print("Start clicked")
        if self.selected_vm:
            self.selected_vm.run()
        # Call this to reload
        self.show_list()

    def on_stop_clicked(self, widget: Gtk.Widget) -> None:
        print("Stop clicked")

    def on_edit_clicked(self, widget: Gtk.Widget) -> None:
        print("Edit clicked")
        self.show_edit()

    def on_select_vm(self, vm: VMBase) -> None:
        print(f"on_select_vm: {vm}")
        if vm is None:
            self.toolbar.set_is_selected(False)
        else:
            self.toolbar.set_is_selected(True)

        self.set_selected(vm)
        self.selected_vm = vm


class ClanListToolbar(Gtk.Toolbar):
    def __init__(
        self,
        *,
        on_start_clicked: Callable[[Gtk.Widget], None],
        on_stop_clicked: Callable[[Gtk.Widget], None],
        on_edit_clicked: Callable[[Gtk.Widget], None],
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.start_button = Gtk.ToolButton(label="Join")
        self.start_button.connect("clicked", on_start_clicked)
        self.add(self.start_button)

        self.edit_button = Gtk.ToolButton(label="Edit")
        self.edit_button.connect("clicked", on_edit_clicked)
        self.add(self.edit_button)

    def set_is_selected(self, s: bool) -> None:
        if s:
            self.edit_button.set_sensitive(True)
            self.start_button.set_sensitive(True)
        else:
            self.edit_button.set_sensitive(False)
            self.start_button.set_sensitive(False)


class ClanEditToolbar(Gtk.Toolbar):
    def __init__(
        self,
        *,
        on_save_clicked: Callable[[Gtk.Widget], None],
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        # Icons See: https://specifications.freedesktop.org/icon-naming-spec/icon-naming-spec-latest.html
        # Could not find a suitable one
        self.save_button = Gtk.ToolButton(label="Save")
        self.save_button.connect("clicked", on_save_clicked)

        self.add(self.save_button)


class ClanListView(Gtk.Box):
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
