from typing import Callable, Any

from gi.repository import Gdk, GdkPixbuf, Gtk, Adw

from ..interfaces import Callbacks
from ..models import VMBase, VMStatus
# from .context_menu import VmMenu


class ClanEditForm(Gtk.Box):
    def __init__(self, *, selected: VMBase | None) -> None:
        super().__init__()
        self.page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        # self.set_border_width(10)
        self.selected = selected
        # self.set_selection_mode(0)

        if self.selected:
            label = Gtk.Box()
            label.append(Gtk.Label.new(f"\n {self.selected.name}"))
            self.append(label)

        # ---------- row 1 --------
        # row = Gtk.ListBoxRow()
        # row_layout = Gtk.Box(spacing=6)

        # # Doc: pack_start/end takes alignment params Expand, Fill, Padding
        # row_layout.append(Gtk.Label.new("Memory Size in MiB"))
        # row_layout.append(
        #     Gtk.SpinButton.new_with_range(512, 4096, 256)
        # )

        # row.append(row_layout)
        # self.append(row)

        # # ----------- row 2 -------

        # row = Gtk.ListBoxRow()
        # row_layout = Gtk.Box(spacing=6)

        # row_layout.append(Gtk.Label("CPU Count"))
        # row_layout.append(Gtk.SpinButton.new_with_range(1, 5, 1))

        # row.append(row_layout)
        # self.append(row)

    def switch(self, widget: Gtk.Widget) -> None:
        self.show_list()


class ClanEdit(Gtk.Box):
    def __init__(
        self, *, remount_list: Callable[[], None], selected_vm: VMBase | None
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, )

        self.show_list = remount_list
        self.selected = selected_vm

        # self.toolbar = ClanEditToolbar(on_save_clicked=self.on_save)
        # self.add(self.toolbar)
        self.append(ClanEditForm(selected=self.selected))

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
        cbs: Callbacks,
        selected_vm: VMBase | None,
        vms: list[VMBase],
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL, )

        self.remount_edit_view = remount_edit
        self.remount_list_view = remount_list
        self.set_selected = set_selected
        self.cbs = cbs
        self.show_join = cbs.show_join

        self.selected_vm: VMBase | None = selected_vm

        # self.toolbar = ClanListToolbar(
        #     selected_vm=selected_vm,
        #     on_start_clicked=self.on_start_clicked,
        #     on_stop_clicked=self.on_stop_clicked,
        #     on_edit_clicked=self.on_edit_clicked,
        #     on_join_clan_clicked=self.on_join_clan_clicked,
        #     on_flash_clicked=self.on_flash_clicked,
        # )
        # self.add(self.toolbar)

        self.append(
            ClanListView(
                vms=vms,
                on_select_row=self.on_select_vm,
                selected_vm=selected_vm,
                on_double_click=self.on_double_click,
            )
        )

    def on_flash_clicked(self, widget: Gtk.Widget) -> None:
        self.cbs.show_flash()

    def on_double_click(self, vm: VMBase) -> None:
        self.on_start_clicked(self)

    def on_start_clicked(self, widget: Gtk.Widget) -> None:
        if self.selected_vm:
            self.cbs.spawn_vm(self.selected_vm.url, self.selected_vm._flake_attr)
        # Call this to reload
        self.remount_list_view()

    def on_stop_clicked(self, widget: Gtk.Widget) -> None:
        if self.selected_vm:
            self.cbs.stop_vm(self.selected_vm.url, self.selected_vm._flake_attr)
        self.remount_list_view()

    def on_join_clan_clicked(self, widget: Gtk.Widget) -> None:
        self.show_join()

    def on_edit_clicked(self, widget: Gtk.Widget) -> None:
        self.remount_edit_view()

    def on_select_vm(self, vm: VMBase) -> None:
        # self.toolbar.set_selected_vm(vm)

        self.set_selected(vm)
        self.selected_vm = vm


class ClanListToolbar(Gtk.Box):
    def __init__(
        self,
        *,
        selected_vm: VMBase | None,
        on_start_clicked: Callable[[Gtk.Widget], None],
        on_stop_clicked: Callable[[Gtk.Widget], None],
        on_edit_clicked: Callable[[Gtk.Widget], None],
        on_join_clan_clicked: Callable[[Gtk.Widget], None],
        on_flash_clicked: Callable[[Gtk.Widget], None],
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL)

        self.start_button = Gtk.ToolButton(label="Start")
        self.start_button.connect("clicked", on_start_clicked)
        self.append(self.start_button)

        self.stop_button = Gtk.ToolButton(label="Stop")
        self.stop_button.connect("clicked", on_stop_clicked)
        self.append(self.stop_button)

        self.edit_button = Gtk.ToolButton(label="Edit")
        self.edit_button.connect("clicked", on_edit_clicked)
        self.append(self.edit_button)

        self.join_clan_button = Gtk.ToolButton(label="Join Clan")
        self.join_clan_button.connect("clicked", on_join_clan_clicked)
        self.append(self.join_clan_button)

        self.flash_button = Gtk.ToolButton(label="Write to USB")
        self.flash_button.connect("clicked", on_flash_clicked)
        self.append(self.flash_button)

        self.set_selected_vm(selected_vm)

    def set_selected_vm(self, vm: VMBase | None) -> None:
        if vm:
            self.edit_button.set_sensitive(True)
            self.start_button.set_sensitive(vm.status == VMStatus.STOPPED)
            self.stop_button.set_sensitive(vm.status == VMStatus.RUNNING)
        else:
            self.edit_button.set_sensitive(False)
            self.start_button.set_sensitive(False)
            self.stop_button.set_sensitive(False)


class ClanEditToolbar(Gtk.Box):
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

        self.append(self.save_button)


class ClanListView(Gtk.Box):
    def __init__(
        self,
        *,
        on_select_row: Callable[[VMBase], None],
        selected_vm: VMBase | None,
        vms: list[VMBase],
        on_double_click: Callable[[VMBase], None],
    ) -> None:
        super().__init__()
        self.vms: list[VMBase] = vms
        self.on_select_row = on_select_row
        self.on_double_click = on_double_click
        # self.context_menu: VmMenu | None = None

        store_types = VMBase.name_to_type_map().values()

        # self.list_store = Gtk.ListStore(*store_types)
        # self.tree_view = Gtk.TreeView(self.list_store)
        # for vm in self.vms:
        #     self.insertVM(vm)

        # setColRenderers(self.tree_view)

        self.set_selected_vm(selected_vm)
        # selection = self.tree_view.get_selection()
        # selection.connect("changed", self._on_select_row)
        # self.tree_view.connect("row-activated", self._on_double_click)
        # self.tree_view.connect("button-press-event", self._on_button_pressed)

        # self.set_border_width(10)
        # self.append(self.tree_view)

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

    # def insertVM(self, vm: VMBase) -> None:
    #     values = list(vm.list_data().values())
    #     icon_idx = VMBase.to_idx("Icon")
    #     values[icon_idx] = GdkPixbuf.Pixbuf.new_from_file_at_scale(
    #         filename=values[icon_idx], width=64, height=64, preserve_aspect_ratio=True
    #     )
    #     self.list_store.append(values)

    def _on_select_row(self, selection: Gtk.TreeSelection) -> None:
        model, row = selection.get_selected()
        if row is not None:
            vm = VMBase(*model[row])
            self.on_select_row(vm)

    # def _on_button_pressed(
    #     self, tree_view: Gtk.TreeView, event: Any
    # ) -> None:
    #     # if self.context_menu:
    #     #     self.context_menu.destroy()
    #     #     self.context_menu = None

    #     if event.button == 3:
    #         path, column, x, y = tree_view.get_path_at_pos(event.x, event.y)
    #         if path is not None:
    #             vm = VMBase(*self.list_store[path[0]])
    #             print(event)
    #             print(f"Right click on {vm.url}")
    #             # self.context_menu = VmMenu(vm)
    #             # self.context_menu.popup_at_pointer(event)

    # def _on_double_click(
    #     self, tree_view: Gtk.TreeView, path: Gtk.TreePath, column: Gtk.TreeViewColumn
    # ) -> None:
    #     # Get the selection object of the tree view
    #     selection = tree_view.get_selection()
    #     model, row = selection.get_selected()

    #     if row is not None:
    #         vm = VMBase(*model[row])
    #         self.on_double_click(vm)


# def setColRenderers(tree_view: Gtk.TreeView) -> None:
#     for idx, (key, gtype) in enumerate(VMBase.name_to_type_map().items()):
#         col: Gtk.TreeViewColumn = None

#         if key.startswith("_"):
#             continue

#         if issubclass(gtype, GdkPixbuf.Pixbuf):
#             renderer = Gtk.CellRendererPixbuf()
#             col = Gtk.TreeViewColumn(key, renderer, pixbuf=idx)
#         elif issubclass(gtype, bool):
#             renderer = Gtk.CellRendererToggle()
#             col = Gtk.TreeViewColumn(key, renderer, active=idx)
#         elif issubclass(gtype, str):
#             renderer = Gtk.CellRendererText()
#             col = Gtk.TreeViewColumn(key, renderer, text=idx)
#         else:
#             raise Exception(f"Unknown type: {gtype}")

#         # CommonSetup for all columns
#         if col:
#             col.set_resizable(True)
#             col.set_expand(True)
#             col.set_property("sizing", Gtk.TreeViewColumnSizing.AUTOSIZE)
#             col.set_property("alignment", 0.5)
#             col.set_sort_column_id(idx)
#             tree_view.append_column(col)
