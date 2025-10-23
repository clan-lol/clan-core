from collections import Counter
from typing import Any, TypeVar, cast

PathTuple = tuple[str, ...]


def list_difference(all_items: list, filter_items: list) -> list:
    """Applys a filter to a list and returns the items in all_items that are not in filter_items

    Example:
    all_items = [1, 2, 3, 4]
    filter_items = [3, 4]

    list_difference(all_items, filter_items) == [1, 2]

    """
    return [value for value in all_items if value not in filter_items]


def find_duplicates(string_list: list[str]) -> list[str]:
    count = Counter(string_list)
    return [item for item, freq in count.items() if freq > 1]


def path_to_string(path: PathTuple) -> str:
    """Convert tuple path to string for display/error messages."""
    return ".".join(str(p) for p in path)


def path_starts_with(path: PathTuple, prefix: PathTuple) -> bool:
    """Check if path starts with prefix tuple."""
    return len(path) >= len(prefix) and path[: len(prefix)] == prefix


type DictLike = dict[str, Any] | Any


def set_value_by_path(d: DictLike, path: str, content: Any) -> None:
    """Update the value at a specific dot-separated path in a nested dictionary.

    If the value didn't exist before, it will be created recursively.

    :param d: The dictionary to update.
    :param path: The dot-separated path to the key (e.g., 'foo.bar').
    :param content: The new value to set.
    """
    keys = path.split(".")
    current = d
    for key in keys[:-1]:
        current = current.setdefault(key, {})
    current[keys[-1]] = content


def set_value_by_path_tuple(d: DictLike, path: PathTuple, content: Any) -> None:
    """Update the value at a specific path in a nested dictionary.

    If the value didn't exist before, it will be created recursively.

    :param d: The dictionary to update.
    :param path: A tuple of strings representing the path to the value.
    :param content: The new value to set.
    """
    keys = path
    current = d
    for key in keys[:-1]:
        current = current.setdefault(key, {})
    current[keys[-1]] = content


def delete_by_path_tuple(d: DictLike, path: PathTuple) -> Any:
    """Deletes the nested entry specified by a dot-separated path from the dictionary using pop().

    :param data: The dictionary to modify.
    :param path: A dot-separated string indicating the nested key to delete.
                 e.g., "foo.bar.baz" will attempt to delete data["foo"]["bar"]["baz"].

    :raises KeyError: If any intermediate key is missing or not a dictionary,
                      or if the final key to delete is not found.
    """
    if not path:
        msg = "Cannot delete. Path is empty."
        raise KeyError(msg)

    keys = path
    current = d

    # Navigate to the parent dictionary of the final key
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            msg = f"Cannot delete. Key '{path_to_string(path)}' not found or not a dictionary '{d}'"
            raise KeyError(msg)
        current = current[key]

    # Attempt to pop the final key
    last_key = keys[-1]
    try:
        value = current.pop(last_key)
    except KeyError:
        # TODO(@hsjobeki): It should be save to raise an error here.
        # Possibly data was already deleted
        # msg = f"Canot delete. Path '{path}' not found in data '{d}'"
        # raise KeyError(msg) from exc
        return {}
    else:
        return {last_key: value}


def delete_by_path(d: dict[str, Any], path: str) -> Any:
    """Deletes the nested entry specified by a dot-separated path from the dictionary using pop().

    :param data: The dictionary to modify.
    :param path: A dot-separated string indicating the nested key to delete.
                 e.g., "foo.bar.baz" will attempt to delete data["foo"]["bar"]["baz"].

    :raises KeyError: If any intermediate key is missing or not a dictionary,
                      or if the final key to delete is not found.
    """
    if not path:
        msg = "Cannot delete. Path is empty."
        raise KeyError(msg)

    keys = path.split(".")
    return delete_by_path_tuple(d, tuple(keys))


V = TypeVar("V")


# TODO: Use PathTuple
def get_value_by_path(
    d: DictLike,
    path: str,
    fallback: V | None = None,
    expected_type: type[V] | None = None,  # noqa: ARG001
) -> V:
    """Get the value at a specific dot-separated path in a nested dictionary.

    If the path does not exist, it returns fallback.

    :param d: The dictionary to get from.
    :param path: The dot-separated path to the key (e.g., 'foo.bar').
    """
    keys = path.split(".")
    current = d
    for key in keys[:-1]:
        current = current.setdefault(key, {})

    if isinstance(current, dict):
        return cast("V", current.get(keys[-1], fallback))

    return cast("V", fallback)


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


def should_skip_path(path: tuple, delete_paths: set[tuple]) -> bool:
    """Check if path should be skipped because it's under a deletion path."""
    return any(path_starts_with(path, delete_path) for delete_path in delete_paths)


# TODO: use PathTuple
def path_match(path: list[str], whitelist_paths: list[list[str]]) -> bool:
    """Returns True if path matches any whitelist path with "*" wildcards.

    I.e.:
    whitelist_paths = [["a.b.*"]]
    path = ["a", "b", "c"]
    path_match(path, whitelist_paths) == True


    whitelist_paths = ["a.b.c", "a.b.*"]
    path = ["a", "b", "d"]
    path_match(path, whitelist_paths) == False
    """
    for wp in whitelist_paths:
        if len(path) != len(wp):
            continue
        match = True
        for p, w in zip(path, wp, strict=False):
            if w not in ("*", p):
                match = False
                break
        if match:
            return True
    return False
