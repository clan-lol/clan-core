from collections.abc import Callable


import gi
gi.require_version("Adw", "1")
from gi.repository import Adw, GdkPixbuf, Gio, GObject, Gtk
from pathlib import Path

from ..models import VMBase, get_initial_vms

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


class VMListItem(GObject.Object):
    def __init__(self, data: VMBase) -> None:
        super().__init__()
        self.data = data

class ClanIcon(Gtk.Box):
    def __init__(self, icon_path: Path) -> None:
        super().__init__()
        self.append(
            GdkPixbuf.Pixbuf.new_from_file_at_scale(
                filename=icon_path, width=64, height=64, preserve_aspect_ratio=True
            )
        )


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
        app: Adw.Application
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.application = app

        boxed_list = Gtk.ListBox()
        boxed_list.set_selection_mode(Gtk.SelectionMode.NONE)
        boxed_list.add_css_class("boxed-list")

        def create_widget(item: VMListItem) -> Gtk.Widget:
            print("Creating", item.data)
            vm = item.data
            # Not displayed; Can be used as id.
            row = Adw.SwitchRow()
            row.set_name(vm.url)
            
            row.set_title(vm.name)
            row.set_title_lines(1)

            row.set_subtitle(vm.url)
            row.set_subtitle_lines(1)

            avatar = Adw.Avatar()
            avatar.set_text(vm.name)
            avatar.set_show_initials(True)
            avatar.set_size(50)
            # (GdkPixbuf.Pixbuf.new_from_file_at_scale(
            #             filename=vm.icon,
            #             width=512,
            #             height=512,
            #             preserve_aspect_ratio=True,
            #         ))
            
            # Gtk.Image.new_from_pixbuf(
                    
            #     )
            row.add_prefix(avatar)


            row.connect("notify::active", self.on_row_toggle)

            return row
        

        list_store = Gio.ListStore()
        print(list_store)

        for vm in get_initial_vms(app.running_vms()):
            list_store.append(VMListItem(data=vm.base))


        boxed_list.bind_model(list_store, create_widget_func=create_widget)

        
        self.append(boxed_list)

    def on_row_toggle(self, row: Adw.SwitchRow, state: bool) -> None:
        print("Toggled", row.get_name(), "active:", row.get_active())
        # TODO: start VM here
        # question: Should we disable the switch 
        # for the time until we got a response for this VM?


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
