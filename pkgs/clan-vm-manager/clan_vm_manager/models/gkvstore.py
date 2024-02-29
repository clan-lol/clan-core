import logging
from collections import OrderedDict
from collections.abc import Callable
from typing import Any, Generic, TypeVar

import gi

gi.require_version("Gio", "2.0")
from gi.repository import Gio, GObject

log = logging.getLogger(__name__)


# Define type variables for key and value types
K = TypeVar("K")  # Key type
V = TypeVar(
    "V", bound=GObject.Object
)  # Value type, bound to GObject.GObject or its subclasses


class GKVStore(GObject.GObject, Gio.ListModel, Generic[K, V]):
    __gtype_name__ = "MyGKVStore"
    """
    A simple key-value store that implements the Gio.ListModel interface, with generic types for keys and values.
    Only use self[key] and del self[key] for accessing the items for better performance.
    This class could be optimized by having the objects remember their position in the list.
    """

    def __init__(self, gtype: type[V], key_gen: Callable[[V], K]) -> None:
        super().__init__()
        self.gtype = gtype
        self.key_gen = key_gen
        self._items: "OrderedDict[K, V]" = OrderedDict()

    @classmethod
    def new(cls: Any, gtype: type[V]) -> "GKVStore":
        return cls.__new__(cls, gtype)

    #########################
    #                       #
    #    READ OPERATIONS    #
    #                       #
    #########################
    def keys(self) -> list[K]:
        return list(self._items.keys())

    def values(self) -> list[V]:
        return list(self._items.values())

    def items(self) -> list[tuple[K, V]]:
        return list(self._items.items())

    def get(self, key: K, default: V | None = None) -> V | None:
        return self._items.get(key, default)

    def get_n_items(self) -> int:
        return len(self._items)

    def do_get_n_items(self) -> int:
        return self.get_n_items()

    def get_item(self, position: int) -> V | None:
        if position < 0 or position >= self.get_n_items():
            return None
        # Access items by index since OrderedDict does not support direct indexing
        key = list(self._items.keys())[position]
        return self._items[key]

    def do_get_item(self, position: int) -> V | None:
        return self.get_item(position)

    def get_item_type(self) -> GObject.GType:
        return self.gtype.__gtype__

    def do_get_item_type(self) -> GObject.GType:
        return self.get_item_type()

    def first(self) -> V:
        return self.values()[0]

    def last(self) -> V:
        return self.values()[-1]

    # O(n) operation
    def find(self, item: V) -> tuple[bool, int]:
        log.warning("Finding is O(n) in GKVStore. Better use indexing")
        for i, v in enumerate(self.values()):
            if v == item:
                return True, i
        return False, -1

    #########################
    #                       #
    #    WRITE OPERATIONS   #
    #                       #
    #########################
    def insert(self, position: int, item: V) -> None:
        key = self.key_gen(item)
        if key in self._items:
            raise ValueError("Key already exists in the dictionary")
        if position < 0 or position > len(self._items):
            raise IndexError("Index out of range")

        # Temporary storage for items to be reinserted
        temp_list = [(k, self._items[k]) for k in list(self.keys())[position:]]

        # Delete items from the original dict
        for k in list(self.keys())[position:]:
            del self._items[k]

        # Insert the new key-value pair
        self._items[key] = item

        # Reinsert the items
        for i, (k, v) in enumerate(temp_list):
            self._items[k] = v

        # Notify the model of the changes
        self.items_changed(position, 0, 1)

    def append(self, item: V) -> None:
        key = self.key_gen(item)
        self[key] = item

    def remove(self, position: int) -> None:
        if position < 0 or position >= self.get_n_items():
            return
        key = self.keys()[position]
        del self[key]
        self.items_changed(position, 1, 0)

    def remove_all(self) -> None:
        self._items.clear()
        self.items_changed(0, len(self._items), 0)

    # O(1) operation if the key does not exist, O(n) if it does
    def __setitem__(self, key: K, value: V) -> None:
        # If the key already exists, remove it O(n)
        if key in self._items:
            log.warning("Updating an existing key in GKVStore is O(n)")
            del self[key]

        # Add the new key-value pair
        self._items[key] = value
        self._items.move_to_end(key)
        position = len(self._items) - 1
        self.items_changed(position, 0, 1)

    # O(n) operation
    def __delitem__(self, key: K) -> None:
        position = self.keys().index(key)
        del self._items[key]
        self.items_changed(position, 1, 0)

    def __len__(self) -> int:
        return len(self._items)

    # O(1) operation
    def __getitem__(self, key: K) -> V:
        return self._items[key]

    def __contains__(self, key: K) -> bool:
        return key in self._items

    def __str__(self) -> str:
        resp = "GKVStore(\n"
        for k, v in self._items.items():
            resp += f"{k}: {v}\n"
        resp += ")"
        return resp

    def __repr__(self) -> str:
        return self._items.__str__()
