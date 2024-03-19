import os
from collections.abc import Callable
from functools import partial
from typing import Any, Literal, TypeVar

import gi

gi.require_version("Adw", "1")
from gi.repository import Adw, Gio, GObject, Gtk

# Define a TypeVar that is bound to GObject.Object
ListItem = TypeVar("ListItem", bound=GObject.Object)


def create_details_list(
    model: Gio.ListStore, render_row: Callable[[Gtk.ListBox, ListItem], Gtk.Widget]
) -> Gtk.ListBox:
    boxed_list = Gtk.ListBox()
    boxed_list.set_selection_mode(Gtk.SelectionMode.NONE)
    boxed_list.add_css_class("boxed-list")
    boxed_list.bind_model(model, create_widget_func=partial(render_row, boxed_list))
    return boxed_list


class PreferencesValue(GObject.Object):
    variant: Literal["CPU", "MEMORY"]
    editable: bool
    data: Any

    def __init__(
        self, variant: Literal["CPU", "MEMORY"], editable: bool, data: Any
    ) -> None:
        super().__init__()
        self.variant = variant
        self.editable = editable
        self.data = data


class Details(Gtk.Box):
    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.VERTICAL)

        preferences_store = Gio.ListStore.new(PreferencesValue)
        preferences_store.append(PreferencesValue("CPU", True, 1))

        self.details_list = create_details_list(
            model=preferences_store, render_row=self.render_entry_row
        )

        self.append(self.details_list)

    def render_entry_row(
        self, boxed_list: Gtk.ListBox, item: PreferencesValue
    ) -> Gtk.Widget:
        cores: int | None = os.cpu_count()
        fcores = float(cores) if cores else 1.0

        row = Adw.SpinRow.new_with_range(0, fcores, 1)
        row.set_value(item.data)

        return row
