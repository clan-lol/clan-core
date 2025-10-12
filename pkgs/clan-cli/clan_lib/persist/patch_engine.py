import json
from typing import Any, TypeVar, cast

from clan_lib.errors import ClanError
from clan_lib.persist.path_utils import (
    PathTuple,
    flatten_data_structured,
    list_difference,
    should_skip_path,
)
from clan_lib.persist.validate import (
    validate_list_uniqueness,
    validate_no_static_deletion,
    validate_patch_conflicts,
    validate_type_compatibility,
    validate_writeability,
)
from clan_lib.persist.write_rules import AttributeMap


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


def calc_patches(
    persisted: dict[str, Any],
    update: dict[str, Any],
    all_values: dict[str, Any],
    attribute_props: AttributeMap,
) -> tuple[dict[PathTuple, Any], set[PathTuple]]:
    """Calculate the patches to apply to the inventory using structured paths.

    Given its current state and the update to apply.
    Calulates the necessary SET patches and DELETE paths.
    While validating persistence rules.

    Args:
        persisted: The current mutable state of the inventory
        update: The update to apply
        all_values: All values in the inventory (static + mutable merged)
        attribute_props: Persistence attribute map, see: 'compute_attribute_map'

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
    # TODO: We currently cannot validate this properly.
    # for delete_path in delete_paths:
    #     for static_path in static_data:
    #         if path_starts_with(static_path, delete_path):
    #             msg = f"Cannot delete path '{path_to_string(delete_path)}' - Readonly path '{path_to_string(static_path)}' is set via .nix file"
    #             raise ClanError(msg)

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
        validate_writeability(path, attribute_props)
        validate_type_compatibility(path, old_value, new_value)
        validate_list_uniqueness(path, new_value)

        patch_value = new_value  # Init

        if isinstance(new_value, list):
            patch_value = list_difference(new_value, static_data.get(path, []))

        patches[path] = patch_value

    validate_patch_conflicts(set(patches.keys()), delete_paths)

    return patches, delete_paths


empty: list[str] = []

T = TypeVar("T")


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
                result[key] = list(dict.fromkeys(curr_val + update_val))  # type: ignore[assignment]
            else:
                result[key] = update_val  # type: ignore[assignment]
        elif (
            update_val is not None
            and curr_val is not None
            and type(update_val) is not type(curr_val)
        ):
            msg = f"Type mismatch for key '{key}'. Cannot update {type(curr_val)} with {type(update_val)}"
            raise ClanError(msg, location=json.dumps([*path, key]))
        elif key in update:
            result[key] = update_val  # type: ignore[assignment]
        elif key in curr:
            result[key] = curr_val  # type: ignore[assignment]

    return cast("T", result)
