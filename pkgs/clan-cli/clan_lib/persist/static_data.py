from typing import Any

from clan_lib.persist.util import flatten_data, list_difference


def calculate_static_data(
    all_values: dict[str, Any], persisted: dict[str, Any]
) -> dict[str, Any]:
    """Calculate the static (read-only) data by finding what exists in all_values
    but not in persisted data.

    This gives us a clear view of what cannot be modified/deleted.
    """
    all_flat = flatten_data(all_values)
    persisted_flat = flatten_data(persisted)
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
