from collections import Counter
from typing import Any, TypedDict

from clan_lib.errors import ClanError

type DictLike = dict[str, Any] | Any

PathTuple = tuple[str, ...]


def list_difference(all_items: list, filter_items: list) -> list:
    """Applys a filter to a list and returns the items in all_items that are not in filter_items

    Example:
    all_items = [1, 2, 3, 4]
    filter_items = [3, 4]

    list_difference(all_items, filter_items) == [1, 2]

    """
    return [value for value in all_items if value not in filter_items]


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


def delete_by_path_tuple(d: dict[str, Any], path: PathTuple) -> Any:
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
    except KeyError as exc:
        # Possibly data was already deleted
        msg = f"Canot delete. Path '{path}' not found in data '{d}'"
        raise KeyError(msg) from exc
        # return {}
    else:
        return {last_key: value}


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


def find_deleted_paths_structured(
    all_values: dict[str, Any],
    update: dict[str, Any],
    parent_key: PathTuple = (),
) -> set[PathTuple]:
    """Find paths that are marked for deletion in the structured format."""
    deleted_paths: set[PathTuple] = set()
    for key, p_value in all_values.items():
        current_path = (*parent_key, key) if parent_key else (key,)
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
                            child_path = (*current_path, child_key)
                            deleted_paths.add(child_path)
                    else:
                        # Both are dicts, recurse deeper
                        deleted_paths |= find_deleted_paths_structured(
                            p_value,
                            u_value,
                            current_path,
                        )
                else:
                    # deleted_paths.add(current_path)

                    # Persisted was a dict, update is not a dict
                    # This can happen if user sets the value to None, explicitly.                    # produce 'set path None' is not a deletion
                    pass

    return deleted_paths


def should_skip_path(path: tuple, delete_paths: set[tuple]) -> bool:
    """Check if path should be skipped because it's under a deletion path."""
    return any(path_starts_with(path, delete_path) for delete_path in delete_paths)


def validate_no_static_deletion(
    path: PathTuple, new_value: Any, static_data: dict[PathTuple, Any]
) -> None:
    """Validate that we're not trying to delete static data."""
    # Check if we're trying to delete a path that exists in static data
    if path in static_data and new_value is None:
        msg = f"Path '{path_to_string(path)}' is readonly - since its defined via a .nix file"
        raise ClanError(msg)

    # For lists, check if we're trying to remove static items
    if isinstance(new_value, list) and path in static_data:
        static_items = static_data[path]
        if isinstance(static_items, list):
            missing_static = [item for item in static_items if item not in new_value]
            if missing_static:
                msg = f"Path '{path_to_string(path)}' doesn't contain static items {missing_static} - They are readonly - since they are defined via a .nix file"
                raise ClanError(msg)


def get_priority(value: Any) -> int | None:
    """Extract priority from a value, handling both dict and non-dict cases."""
    if isinstance(value, dict) and "__prio" in value:
        return value["__prio"]
    return None


def is_mergeable_type(value: Any) -> bool:
    """Check if a value type supports merging (dict or list)."""
    return isinstance(value, (dict, list))


def should_inherit_non_writeable(
    priority: int | None, parent_non_writeable: bool
) -> bool:
    """Determine if this node should be marked as non-writeable due to inheritance."""
    if parent_non_writeable:
        return True

    return priority is not None and priority < WRITABLE_PRIORITY_THRESHOLD


def is_key_writeable(
    priority: int | None, exists_in_persisted: bool, value_in_all: Any
) -> bool:
    """Determine if a key is writeable based on priority and mergeability rules.

    Rules:
    - Priority > 100: Always writeable
    - Priority < 100: Never writeable
    - Priority == 100: Writeable if mergeable (dict/list) OR exists in persisted
    """
    if priority is None:
        return False  # No priority means not writeable

    if priority > WRITABLE_PRIORITY_THRESHOLD:
        return True

    if priority < WRITABLE_PRIORITY_THRESHOLD:
        return False

    # priority == WRITABLE_PRIORITY_THRESHOLD (100)
    return is_mergeable_type(value_in_all) or exists_in_persisted


WRITABLE_PRIORITY_THRESHOLD = 100  # Values below this are not writeable


class WriteabilityResult(TypedDict):
    writeable: set[PathTuple]
    non_writeable: set[PathTuple]


def _determine_writeability_recursive(
    priorities: dict[str, Any],
    all_values: dict[str, Any],
    persisted: dict[str, Any],
    current_path: PathTuple = (),
    inherited_priority: int | None = None,
    parent_non_writeable: bool = False,
    results: WriteabilityResult | None = None,
) -> WriteabilityResult:
    """Recursively determine writeability for all paths in the priority structure.

    This is internal recursive function. Use 'determine_writeability' as entry point.
    """
    if results is None:
        results = WriteabilityResult(writeable=set(), non_writeable=set())

    for key, value in priorities.items():
        # Skip metadata keys
        if key == "__prio":
            continue

        path = (*current_path, key)

        # Determine priority for this key
        key_priority = get_priority(value)
        effective_priority = (
            key_priority if key_priority is not None else inherited_priority
        )

        # Check if this should be non-writeable due to inheritance
        force_non_writeable = should_inherit_non_writeable(
            effective_priority, parent_non_writeable
        )

        if force_non_writeable:
            results["non_writeable"].add(path)
            # All children are also non-writeable
            if isinstance(value, dict):
                _determine_writeability_recursive(
                    value,
                    all_values.get(key, {}),
                    {},  # Doesn't matter since all children will be non-writeable
                    path,
                    effective_priority,
                    parent_non_writeable=True,
                    results=results,
                )
        else:
            # Determine writeability based on rules
            if effective_priority is None:
                msg = f"Priority for path '{path_to_string(path)}' is not defined. Cannot determine writeability."
                raise ClanError(msg)

            exists_in_persisted = key in persisted
            value_in_all = all_values.get(key)

            if is_key_writeable(effective_priority, exists_in_persisted, value_in_all):
                results["writeable"].add(path)
            else:
                results["non_writeable"].add(path)

            # Recurse into children
            if isinstance(value, dict):
                _determine_writeability_recursive(
                    value,
                    all_values.get(key, {}),
                    persisted.get(key, {}),
                    path,
                    effective_priority,
                    parent_non_writeable=False,
                    results=results,
                )

    return results


def determine_writeability(
    priorities: dict[str, Any], all_values: dict[str, Any], persisted: dict[str, Any]
) -> WriteabilityResult:
    """Determine writeability for all paths based on priorities and current data.

    - Priority-based writeability: Values with priority < 100 are not writeable
    - Inheritance: Children inherit parent priorities if not specified
    - Special case at priority 100: Can be writeable if it's mergeable (dict/list) or exists in persisted data

    Args:
        priorities: The priority structure defining writeability rules. See: 'clanInternals.inventoryClass.introspection'
        all_values: All values in the inventory, See: 'clanInternals.inventoryClass.allValues'
        persisted: The current mutable state of the inventory, see: 'readFile inventory.json'

    Returns:
        Dict with sets of writeable and non-writeable paths using tuple keys

    """
    return _determine_writeability_recursive(priorities, all_values, persisted)


def find_duplicates(string_list: list[str]) -> list[str]:
    count = Counter(string_list)
    return [item for item, freq in count.items() if freq > 1]


def is_writeable_path(
    key: PathTuple,
    writeables: WriteabilityResult,
) -> bool:
    """Recursively check if a key is writeable.

    If key "machines.machine1.deploy.targetHost" is specified but writeability is only
    defined for "machines", we pop the last key and check if the parent key is writeable/non-writeable.
    """
    remaining = key
    while remaining:
        current_path = remaining
        if current_path in writeables["writeable"]:
            return True
        if current_path in writeables["non_writeable"]:
            return False
        remaining = remaining[:-1]

    msg = f"Cannot determine writeability for key '{key}'"
    raise ClanError(msg)


def validate_writeability(path: PathTuple, writeables: WriteabilityResult) -> None:
    """Validate that a path is writeable."""
    if not is_writeable_path(path, writeables):
        msg = f"Path '{path_to_string(path)}' is readonly. - It seems its value is statically defined in nix."
        raise ClanError(msg)


def validate_type_compatibility(path: tuple, old_value: Any, new_value: Any) -> None:
    """Validate that type changes are allowed."""
    if old_value is not None and type(old_value) is not type(new_value):
        if new_value is None:
            return  # Deletion is handled separately

        path_str = path_to_string(path)
        msg = f"Type mismatch for path '{path_str}'. Cannot update {type(old_value)} with {type(new_value)}"
        description = f"""
Previous value is of type '{type(old_value)}' this operation would change it to '{type(new_value)}'.
Prev: {old_value}
->
After: {new_value}
        """
        raise ClanError(msg, description=description)


def validate_list_uniqueness(path: tuple, value: Any) -> None:
    """Validate that lists don't contain duplicates."""
    if isinstance(value, list):
        duplicates = find_duplicates(value)
        if duplicates:
            msg = f"Path '{path_to_string(path)}' contains list duplicates: {duplicates} - List values must be unique."
            raise ClanError(msg)


def validate_patch_conflicts(
    patches: set[PathTuple], delete_paths: set[PathTuple]
) -> None:
    """Ensure patches don't conflict with deletions."""
    conflicts = {
        path
        for delete_path in delete_paths
        for path in patches
        if path_starts_with(path, delete_path)
    }

    if conflicts:
        conflict_list = ", ".join(path_to_string(path) for path in sorted(conflicts))
        msg = f"The following paths are marked for deletion but also have update values: {conflict_list}. - You cannot delete and patch the same path and its subpaths."
        raise ClanError(msg)


def calc_patches(
    persisted: dict[str, Any],
    update: dict[str, Any],
    all_values: dict[str, Any],
    writeables: WriteabilityResult,
) -> tuple[dict[PathTuple, Any], set[PathTuple]]:
    """Calculate the patches to apply to the inventory using structured paths.

    Given its current state and the update to apply.
    Calulates the necessary SET patches and DELETE paths.
    While validating writeability rules.

    Args:
        persisted: The current mutable state of the inventory
        update: The update to apply
        all_values: All values in the inventory (static + mutable merged)
        writeables: The writeable keys. Use 'determine_writeability'.
                   Example: {'writeable': {'foo', 'foo.bar'}, 'non_writeable': {'foo.nix'}}

    Returns:
        Tuple of (SET patches dict, DELETE paths set)

    Raises:
        ClanError: When validation fails or invalid operations are attempted

    """
    # Calculate static data using structured paths
    static_data = calculate_static_data(all_values, persisted)

    # Flatten all data structures using structured paths
    # persisted_flat = flatten_data_structured(persisted)
    update_flat = flatten_data_structured(update)
    all_values_flat = flatten_data_structured(all_values)

    # Early validation: ensure we're not trying to modify static-only paths
    # validate_no_static_modification(update_flat, static_data)

    # Find paths marked for deletion
    delete_paths = find_deleted_paths_structured(all_values, update)

    # Validate deletions don't affect static data
    for delete_path in delete_paths:
        for static_path in static_data:
            if path_starts_with(static_path, delete_path):
                msg = f"Cannot delete path '{path_to_string(delete_path)}' - Readonly path '{path_to_string(static_path)}' is set via .nix file"
                raise ClanError(msg)

    # Get all paths that might need processing
    all_paths: set[PathTuple] = set(all_values_flat) | set(update_flat)

    # Calculate patches
    patches: dict[PathTuple, Any] = {}
    for path in all_paths:
        old_value = all_values_flat.get(path)
        new_value = update_flat.get(path)
        has_value = path in update_flat

        # Skip if no change
        if old_value == new_value:
            continue

        # Skip if path is marked for deletion or under a deletion path
        if should_skip_path(path, delete_paths):
            continue

        # Skip deletions (they're handled by delete_paths)
        if old_value is not None and not has_value:
            continue

        # Validate the change is allowed
        validate_no_static_deletion(path, new_value, static_data)
        validate_writeability(path, writeables)
        validate_type_compatibility(path, old_value, new_value)
        validate_list_uniqueness(path, new_value)

        patch_value = new_value  # Init

        if isinstance(new_value, list):
            patch_value = list_difference(new_value, static_data.get(path, []))

        patches[path] = patch_value

    validate_patch_conflicts(set(patches.keys()), delete_paths)

    return patches, delete_paths
