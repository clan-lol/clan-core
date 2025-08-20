"""Utilities for working with nested dictionaries, particularly for
flattening, unmerging lists, finding duplicates, and calculating patches.
"""

import json
from collections import Counter
from typing import Any, TypeVar, cast

from clan_lib.errors import ClanError

T = TypeVar("T")

empty: list[str] = []


def merge_objects(
    curr: T,
    update: T,
    merge_lists: bool = True,
    path: list[str] = empty,
) -> T:
    """Updates values in curr by values of update
    The output contains values for all keys of curr and update together.

    Lists are deduplicated and appended almost like in the nix module system.

    Example:
    merge_objects({"a": 1}, {"a": null }) -> {"a": null}
    merge_objects({"a": null}, {"a": 1 }) -> {"a": 1}

    """
    result = {}
    msg = f"cannot update non-dictionary values: {curr} by {update}"
    if not isinstance(update, dict):
        raise ClanError(msg)
    if not isinstance(curr, dict):
        raise ClanError(msg)

    all_keys = set(update.keys()).union(curr.keys())

    for key in all_keys:
        curr_val = curr.get(key)
        update_val = update.get(key)

        if isinstance(update_val, dict) and isinstance(curr_val, dict):
            result[key] = merge_objects(
                curr_val,
                update_val,
                merge_lists=merge_lists,
                path=[*path, key],
            )
        elif isinstance(update_val, list) and isinstance(curr_val, list):
            if merge_lists:
                result[key] = list(dict.fromkeys(curr_val + update_val))  # type: ignore
            else:
                result[key] = update_val  # type: ignore
        elif (
            update_val is not None
            and curr_val is not None
            and type(update_val) is not type(curr_val)
        ):
            msg = f"Type mismatch for key '{key}'. Cannot update {type(curr_val)} with {type(update_val)}"
            raise ClanError(msg, location=json.dumps([*path, key]))
        elif key in update:
            result[key] = update_val  # type: ignore
        elif key in curr:
            result[key] = curr_val  # type: ignore

    return cast("T", result)


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


def flatten_data(data: dict, parent_key: str = "", separator: str = ".") -> dict:
    """Recursively flattens a nested dictionary structure where keys are joined by the separator.

    Args:
        data (dict): The nested dictionary structure.
        parent_key (str): The current path to the nested dictionary (used for recursion).
        separator (str): The string to use for joining keys.

    Returns:
        dict: A flattened dictionary with all values. Directly in the root.

    """
    flattened = {}

    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key

        if isinstance(value, dict):
            # Recursively flatten the nested dictionary
            if value:
                flattened.update(flatten_data(value, new_key, separator))
            else:
                # If the value is an empty dictionary, add it to the flattened dict
                flattened[new_key] = {}
        else:
            flattened[new_key] = value

    return flattened


def list_difference(all_items: list, filter_items: list) -> list:
    """Unmerge the current list. Given a previous list.

    Returns:
        The other list.

    """
    # Unmerge the lists
    return [value for value in all_items if value not in filter_items]


def find_duplicates(string_list: list[str]) -> list[str]:
    count = Counter(string_list)
    duplicates = [item for item, freq in count.items() if freq > 1]
    return duplicates


def find_deleted_paths(
    curr: dict[str, Any],
    update: dict[str, Any],
    parent_key: str = "",
) -> set[str]:
    """Recursively find keys (at any nesting level) that exist in persisted but do not
    exist in update. If a nested dictionary is completely removed, return that dictionary key.

    :param persisted: The original (persisted) nested dictionary.
    :param update: The updated nested dictionary (some keys might be removed).
    :param parent_key: The dotted path to the current dictionary's location.
    :return: A set of dotted paths indicating keys or entire nested paths that were deleted.
    """
    deleted_paths = set()

    # Iterate over keys in persisted
    for key, p_value in curr.items():
        current_path = f"{parent_key}.{key}" if parent_key else key
        # Check if this key exists in update
        if key not in update:
            # Key doesn't exist at all -> entire branch deleted
            deleted_paths.add(current_path)
        else:
            u_value = update[key]
            # If persisted value is dict, check the update value
            if isinstance(p_value, dict):
                if isinstance(u_value, dict):
                    # If persisted dict is non-empty but updated dict is empty,
                    # that means everything under this branch is removed.
                    if p_value and not u_value:
                        # All children are removed
                        for child_key in p_value:
                            child_path = f"{current_path}.{child_key}"
                            deleted_paths.add(child_path)
                    else:
                        # Both are dicts, recurse deeper
                        deleted_paths |= find_deleted_paths(
                            p_value,
                            u_value,
                            current_path,
                        )
                else:
                    # Persisted was a dict, update is not a dict -> entire branch changed
                    # Consider this as a full deletion of the persisted branch
                    deleted_paths.add(current_path)

    return deleted_paths


def parent_is_dict(key: str, data: dict[str, Any]) -> bool:
    parts = key.split(".")
    while len(parts) > 1:
        parts.pop()
        parent_key = ".".join(parts)
        if parent_key in data:
            return isinstance(data[parent_key], dict)
    return False


def is_writeable_key(
    key: str,
    writeables: dict[str, set[str]],
) -> bool:
    """Recursively check if a key is writeable.
    key "machines.machine1.deploy.targetHost" is specified but writeability is only defined for "machines"
    We pop the last key and check if the parent key is writeable/non-writeable.
    """
    remaining = key.split(".")
    while remaining:
        if ".".join(remaining) in writeables["writeable"]:
            return True
        if ".".join(remaining) in writeables["non_writeable"]:
            return False

        remaining.pop()

    msg = f"Cannot determine writeability for key '{key}'"
    raise ClanError(msg, description="F001")


def calc_patches(
    persisted: dict[str, Any],
    update: dict[str, Any],
    all_values: dict[str, Any],
    writeables: dict[str, set[str]],
) -> tuple[dict[str, Any], set[str]]:
    """Calculate the patches to apply to the inventory.

    Given its current state and the update to apply.

    Filters out nix-values so it doesn't matter if the anyone sends them.

    : param persisted: The current state of the inventory.
    : param update: The update to apply.
    : param writeable: The writeable keys. Use 'determine_writeability'.
        Example: {'writeable': {'foo', 'foo.bar'}, 'non_writeable': {'foo.nix'}}
    : param all_values: All values in the inventory retrieved from the flake evaluation.

    Returns a tuple with the SET and DELETE patches.
    """
    data_all = flatten_data(all_values)
    data_all_updated = flatten_data(update)
    data_dyn = flatten_data(persisted)

    all_keys = set(data_all) | set(data_all_updated)
    patchset = {}

    delete_set = find_deleted_paths(all_values, update, parent_key="")

    for key in all_keys:
        # Get the old and new values
        old = data_all.get(key, None)
        new = data_all_updated.get(key, None)

        # Some kind of change
        if old != new:
            # If there is a change, check if the key is writeable
            if not is_writeable_key(key, writeables):
                msg = f"Key '{key}' is not writeable. It seems its value is statically defined in nix."
                raise ClanError(msg)

            if any(key.startswith(d) for d in delete_set):
                # Skip this key if it or any of its parent paths are marked for deletion
                continue

            if old is not None and type(old) is not type(new):
                if new is None:
                    # If this is a deleted key, they are handled by 'find_deleted_paths'
                    continue

                msg = f"Type mismatch for key '{key}'. Cannot update {type(old)} with {type(new)}"
                description = f"""
Previous_value is of type '{type(old)}' this operation would change it to '{type(new)}'.

Prev: {old}
->
After: {new}
"""
                raise ClanError(msg, description=description)

            if isinstance(new, list):
                duplicates = find_duplicates(new)
                if duplicates:
                    msg = f"Key '{key}' contains list duplicates: {duplicates} - List values must be unique."
                    raise ClanError(msg)
                # List of current values
                persisted_data = data_dyn.get(key, [])
                # List including nix values
                all_list = data_all.get(key, [])
                nix_list = list_difference(all_list, persisted_data)

                # every item in nix_list MUST be in new
                nix_items_to_remove = list(
                    filter(lambda item: item not in new, nix_list),
                )

                if nix_items_to_remove:
                    msg = (
                        f"Key '{key}' doesn't contain items {nix_items_to_remove} - "
                        "Deleting them is not possible, they are static values set via a .nix file"
                    )
                    raise ClanError(msg)

                if new != all_list:
                    patchset[key] = list_difference(new, nix_list)
            else:
                patchset[key] = new

    # Ensure not inadvertently patching something already marked for deletion
    conflicts = {key for d in delete_set for key in patchset if key.startswith(d)}
    if conflicts:
        conflict_list = ", ".join(sorted(conflicts))
        msg = (
            f"The following keys are marked for deletion but also have update values: {conflict_list}. "
            "You cannot delete and patch the same key and its subkeys."
        )
        raise ClanError(msg)
    return patchset, delete_set


def determine_writeability(
    priorities: dict[str, Any],
    defaults: dict[str, Any],
    persisted: dict[str, Any],
    parent_key: str = "",
    parent_prio: int | None = None,
    results: dict | None = None,
    non_writeable: bool = False,
) -> dict[str, set[str]]:
    if results is None:
        results = {"writeable": set({}), "non_writeable": set({})}

    for key, value in priorities.items():
        if key == "__prio":
            continue

        full_key = f"{parent_key}.{key}" if parent_key else key

        # Determine the priority for the current key
        # Inherit from parent if no priority is defined
        prio = value.get("__prio", None)
        if prio is None:
            prio = parent_prio

        # If priority is less than 100, all children are not writeable
        # If the parent passed "non_writeable" earlier, this makes all children not writeable
        if (prio is not None and prio < 100) or non_writeable:
            results["non_writeable"].add(full_key)
            if isinstance(value, dict):
                determine_writeability(
                    value,
                    defaults,
                    {},  # Children won't be writeable, so correlation doesn't matter here
                    full_key,
                    prio,  # Pass the same priority down
                    results,
                    # Recursively mark all children as non-writeable
                    non_writeable=True,
                )
            continue

        # Check if the key is writeable otherwise
        key_in_correlated = key in persisted
        if prio is None:
            msg = f"Priority for key '{full_key}' is not defined. Cannot determine if it is writeable."
            raise ClanError(msg)

        is_mergeable = False
        if prio == 100:
            default = defaults.get(key)
            if isinstance(default, dict):
                is_mergeable = True
            if isinstance(default, list):
                is_mergeable = True
            if key_in_correlated:
                is_mergeable = True

        is_writeable = prio > 100 or is_mergeable

        # Append the result
        if is_writeable:
            results["writeable"].add(full_key)
        else:
            results["non_writeable"].add(full_key)

        # Recursive
        if isinstance(value, dict):
            determine_writeability(
                value,
                defaults.get(key, {}),
                persisted.get(key, {}),
                full_key,
                prio,  # Pass down current priority
                results,
            )

    return results


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
    current = d

    # Navigate to the parent dictionary of the final key
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            msg = f"Cannot delete. Key '{path}' not found or not a dictionary '{d}'"
            raise KeyError(msg)
        current = current[key]

    # Attempt to pop the final key
    last_key = keys[-1]
    try:
        value = current.pop(last_key)
    except KeyError as exc:
        msg = f"Cannot delete. Path '{path}' not found in data '{d}'"
        raise KeyError(msg) from exc
    else:
        return {last_key: value}


type DictLike = dict[str, Any] | Any


def get_value_by_path(d: DictLike, path: str, fallback: Any = None) -> Any:
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
        return current.get(keys[-1], fallback)

    return fallback


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


from typing import NotRequired, Required, get_args, get_origin, get_type_hints


def is_typeddict_class(obj: type) -> bool:
    """Safely checks if a class is a TypedDict."""
    return (
        isinstance(obj, type)
        and hasattr(obj, "__annotations__")
        and obj.__class__.__name__ == "_TypedDictMeta"
    )


def retrieve_typed_field_names(obj: type, prefix: str = "") -> set[str]:
    fields = set()
    hints = get_type_hints(obj, include_extras=True)

    for field, field_type in hints.items():
        full_key = f"{prefix}.{field}" if prefix else field

        origin = get_origin(field_type)
        args = get_args(field_type)

        # Unwrap Required/NotRequired
        if origin in {NotRequired, Required}:
            field_type = args[0]
            origin = get_origin(field_type)
            args = get_args(field_type)

        if is_typeddict_class(field_type):
            fields |= retrieve_typed_field_names(field_type, prefix=full_key)
        else:
            fields.add(full_key)

    return fields
