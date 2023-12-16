from collections.abc import Callable

from gi.repository import GdkPixbuf, Gtk

from ..models import VMBase, get_initial_vms


class ClanEditForm(Gtk.ListBox):
    def __init__(self, *, selected: VMBase | None) -> None:
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
    def __init__(
        self, *, remount_list: Callable[[], None], selected_vm: VMBase | None
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, expand=True)

        self.show_list = remount_list
        self.selected = selected_vm

        button_hooks = {
            "on_save_clicked": self.on_save,
        }

        self.toolbar = ClanEditToolbar(**button_hooks)
        self.add(self.toolbar)
        self.add(ClanEditForm(selected=self.selected))

    def on_save(self, widget: Gtk.Widget) -> None:
        print("Save clicked saving values")
        self.show_list()


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

    def __init__(
        self,
        *,
        remount_list: Callable[[], None],
        remount_edit: Callable[[], None],
        set_selected: Callable[[VMBase | None], None],
        selected_vm: VMBase | None,
        show_toolbar: bool = True,
        show_join: Callable[[], None],
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, expand=True)

        self.remount_edit_view = remount_edit
        self.remount_list_view = remount_list
        self.set_selected = set_selected
        self.show_toolbar = show_toolbar
        self.show_join = show_join

        self.selected_vm: VMBase | None = selected_vm

        button_hooks = {
            "on_start_clicked": self.on_start_clicked,
            "on_stop_clicked": self.on_stop_clicked,
            "on_edit_clicked": self.on_edit_clicked,
            "on_join_clicked": self.on_join_clicked,
        }
        if show_toolbar:
            self.toolbar = ClanListToolbar(**button_hooks)
            self.toolbar.set_is_selected(self.selected_vm is not None)
            self.add(self.toolbar)

        self.list_hooks = {
            "on_select_row": self.on_select_vm,
        }
        self.add(ClanListView(**self.list_hooks, selected_vm=selected_vm))

    def on_start_clicked(self, widget: Gtk.Widget) -> None:
        print("Start clicked")
        if self.selected_vm:
            self.selected_vm.run()
        # Call this to reload
        self.remount_list_view()

    def on_stop_clicked(self, widget: Gtk.Widget) -> None:
        print("Stop clicked")

    def on_join_clicked(self, widget: Gtk.Widget) -> None:
        print("Join clicked")
        self.show_join()

    def on_edit_clicked(self, widget: Gtk.Widget) -> None:
        print("Edit clicked")
        self.remount_edit_view()

    def on_select_vm(self, vm: VMBase) -> None:
        print(f"on_select_vm: {vm.name}")
        if self.show_toolbar:
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
        on_join_clicked: Callable[[Gtk.Widget], None],
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.start_button = Gtk.ToolButton(label="Start")
        self.start_button.connect("clicked", on_start_clicked)
        self.add(self.start_button)

        self.stop_button = Gtk.ToolButton(label="Stop")
        self.stop_button.connect("clicked", on_stop_clicked)
        self.add(self.stop_button)

        self.edit_button = Gtk.ToolButton(label="Edit")
        self.edit_button.connect("clicked", on_edit_clicked)
        self.add(self.edit_button)

        self.join_button = Gtk.ToolButton(label="New")
        self.join_button.connect("clicked", on_join_clicked)
        self.add(self.join_button)

    def set_is_selected(self, s: bool) -> None:
        if s:
            self.edit_button.set_sensitive(True)
            self.start_button.set_sensitive(True)
            self.stop_button.set_sensitive(True)
        else:
            self.edit_button.set_sensitive(False)
            self.start_button.set_sensitive(False)
            self.stop_button.set_sensitive(False)


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
        on_select_row: Callable[[VMBase], None],
        selected_vm: VMBase | None,
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

        self.set_selected_vm(selected_vm)
        selection = self.tree_view.get_selection()
        selection.connect("changed", self._on_select_row)
        self.tree_view.connect("row-activated", self._on_double_click)

        self.set_border_width(10)
        self.add(self.tree_view)

    def find_vm(self, vm: VMBase) -> int:
        for idx, row in enumerate(self.list_store):
            if row[VMBase.to_idx("Name")] == vm.name:  # TODO: Change to path
                return idx
        return -1

    def set_selected_vm(self, vm: VMBase | None) -> None:
        if vm is None:
            return
        selection = self.tree_view.get_selection()
        idx = self.find_vm(vm)
        selection.select_path(idx)

    def insertVM(self, vm: VMBase) -> None:
        values = list(vm.list_data().values())
        icon_idx = VMBase.to_idx("Icon")
        values[icon_idx] = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            filename=values[icon_idx], width=64, height=64, preserve_aspect_ratio=True
        )
        self.list_store.append(values)

    def _on_select_row(self, selection: Gtk.TreeSelection) -> None:
        model, row = selection.get_selected()
        if row is not None:
            vm = VMBase(*model[row])
            self.on_select_row(vm)

    def _on_double_click(
        self, tree_view: Gtk.TreeView, path: Gtk.TreePath, column: Gtk.TreeViewColumn
    ) -> None:
        # Get the selection object of the tree view
        selection = tree_view.get_selection()
        model, row = selection.get_selected()
        if row is not None:
            vm = VMBase(*model[row])
            vm.run()


def setColRenderers(tree_view: Gtk.TreeView) -> None:
    for idx, (key, gtype) in enumerate(VMBase.name_to_type_map().items()):
        col: Gtk.TreeViewColumn = None

        if key.startswith("_"):
            continue

        if issubclass(gtype, GdkPixbuf.Pixbuf):
            renderer = Gtk.CellRendererPixbuf()
            col = Gtk.TreeViewColumn(key, renderer, pixbuf=idx)
        elif issubclass(gtype, bool):
            renderer = Gtk.CellRendererToggle()
            col = Gtk.TreeViewColumn(key, renderer, active=idx)
        elif issubclass(gtype, str):
            renderer = Gtk.CellRendererText()
            col = Gtk.TreeViewColumn(key, renderer, text=idx)
        else:
            raise Exception(f"Unknown type: {gtype}")

        # CommonSetup for all columns
        if col:
            col.set_resizable(True)
            col.set_expand(True)
            col.set_property("sizing", Gtk.TreeViewColumnSizing.AUTOSIZE)
            col.set_property("alignment", 0.5)
            col.set_sort_column_id(idx)
            tree_view.append_column(col)
