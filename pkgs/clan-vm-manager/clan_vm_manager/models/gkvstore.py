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
    "V", bound=GObject.GObject
)  # Value type, bound to GObject.GObject or its subclasses


class GKVStore(GObject.GObject, Gio.ListModel, Generic[K, V]):
    """
    A simple key-value store that implements the Gio.ListModel interface, with generic types for keys and values.
    Only use self[key] and del self[key] for accessing the items for better performance.
    This class could be optimized by having the objects remember their position in the list.
    """

    def __init__(self, gtype: GObject.GType, key_gen: Callable[[V], K]) -> None:
        super().__init__()
        self.gtype = gtype
        self.key_gen = key_gen
        self._items: "OrderedDict[K, V]" = OrderedDict()

    # The rest of your class implementation...

    @classmethod
    def new(cls: Any, gtype: GObject.GType) -> "GKVStore":
        return cls.__new__(cls, gtype)

    def get_n_items(self) -> int:
        return len(self._items)

    def get_item(self, position: int) -> V | None:
        if position < 0 or position >= self.get_n_items():
            return None
        # Access items by index since OrderedDict does not support direct indexing
        key = list(self._items.keys())[position]
        return self._items[key]

    def get_item_type(self) -> GObject.GType:
        return self.gtype

    def insert(self, position: int, item: V) -> None:
        key = self.key_gen(item)
        if key in self._items:
            raise ValueError("Key already exists in the dictionary")
        if position < 0 or position > len(self._items):
            raise IndexError("Index out of range")

        # Temporary storage for items to be reinserted
        temp_list = [(k, self._items[k]) for k in list(self._items.keys())[position:]]
        # Delete items from the original dict
        for k in list(self._items.keys())[position:]:
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
        self._items[key] = item

    def remove(self, position: int) -> None:
        if position < 0 or position >= self.get_n_items():
            return
        key = list(self._items.keys())[position]
        del self._items[key]
        self.items_changed(position, 1, 0)

    def remove_all(self) -> None:
        self._items.clear()
        self.items_changed(0, len(self._items), 0)

    # O(n) operation
    def find(self, item: V) -> tuple[bool, int]:
        log.debug("Finding is O(n) in GKVStore. Better use indexing")
        for i, v in enumerate(self._items.values()):
            if v == item:
                return True, i
        return False, -1

    def first(self) -> V:
        res = next(iter(self._items.values()))
        if res is None:
            raise ValueError("The store is empty")
        return res

    def last(self) -> V:
        res = next(reversed(self._items.values()))
        if res is None:
            raise ValueError("The store is empty")
        return res

    # O(1) operation if the key does not exist, O(n) if it does
    def __setitem__(self, key: K, value: V) -> None:
        # If the key already exists, remove it O(n)
        if key in self._items:
            position = list(self._items.keys()).index(key)
            del self._items[key]
            self.items_changed(position, 1, 0)

        # Add the new key-value pair
        self._items[key] = value
        self._items.move_to_end(key)
        position = len(self._items) - 1
        self.items_changed(position, 0, 1)

    # O(n) operation
    def __delitem__(self, key: K) -> None:
        position = list(self._items.keys()).index(key)
        del self._items[key]
        self.items_changed(position, 1, 0)

    # O(1) operation
    def __getitem__(self, key: K) -> V:
        return self._items[key]

    def sort(self) -> None:
        raise NotImplementedError("Sorting is not supported")

    def find_with_equal_func(self, item: V, equal_func: Callable[[V, V], bool]) -> int:
        raise NotImplementedError("Finding is not supported")

    def find_with_equal_func_full(
        self, item: V, equal_func: Callable[[V, V], bool], user_data: object | None
    ) -> int:
        raise NotImplementedError("Finding is not supported")

    def insert_sorted(
        self, item: V, compare_func: Callable[[V, V], int], user_data: object | None
    ) -> None:
        raise NotImplementedError("Sorting is not supported")

    def splice(self, position: int, n_removals: int, additions: list[V]) -> None:
        raise NotImplementedError("Splicing is not supported")
