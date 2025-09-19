from typing import Any

from clan_lib.errors import ClanError
from clan_lib.persist.util import list_difference

PathTuple = tuple[str, ...]


def path_to_string(path: PathTuple) -> str:
    """Convert tuple path to string for display/error messages."""
    return ".".join(str(p) for p in path)


def path_starts_with(path: PathTuple, prefix: PathTuple) -> bool:
    """Check if path starts with prefix tuple."""
    return len(path) >= len(prefix) and path[: len(prefix)] == prefix


def flatten_data_structured(
    data: dict, parent_path: PathTuple = ()
) -> dict[PathTuple, Any]:
    """Flatten data using tuple keys instead of string concatenation.
    This eliminates ambiguity between literal dots in keys vs nested structure.

    Args:
        data: The nested dictionary to flatten
        parent_path: Current path as tuple (used for recursion)

    Returns:
        Dict with tuple keys representing the full path to each value

    Example:
        {"key.foo": "val1", "key": {"foo": "val2"}}
        becomes:
        {("key.foo",): "val1", ("key", "foo"): "val2"}

    """
    flattened = {}
    for key, value in data.items():
        current_path = (*parent_path, key)

        if isinstance(value, dict):
            if value:
                flattened.update(flatten_data_structured(value, current_path))
            else:
                flattened[current_path] = {}
        else:
            flattened[current_path] = value
    return flattened


def calculate_static_data(
    all_values: dict[str, Any], persisted: dict[str, Any]
) -> dict[PathTuple, Any]:
    """Calculate the static (read-only) data by finding what exists in all_values
    but not in persisted data.

    This gives us a clear view of what cannot be modified/deleted.
    """
    all_flat = flatten_data_structured(all_values)
    persisted_flat = flatten_data_structured(persisted)
    static_flat = {}

    for key, value in all_flat.items():
        if key not in persisted_flat:
            # This key exists only in static data
            static_flat[key] = value
        elif isinstance(value, list) and isinstance(persisted_flat[key], list):
            # For lists, find items that are only in all_values (static items)
            static_items = list_difference(value, persisted_flat[key])
            if static_items:
                static_flat[key] = static_items

    return static_flat
