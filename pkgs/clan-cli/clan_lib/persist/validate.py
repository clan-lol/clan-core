from typing import Any

from clan_lib.errors import ClanError
from clan_lib.persist.path_utils import (
    PathTuple,
    find_duplicates,
    path_starts_with,
    path_to_string,
)
from clan_lib.persist.write_rules import AttributeMap, is_writeable_path


def validate_no_static_deletion(
    path: PathTuple, new_list: list[Any], static_items: list[Any]
) -> None:
    """Validate that we're not trying to delete static items from a list."""
    missing_static = [item for item in static_items if item not in new_list]
    if missing_static:
        msg = f"Path '{path_to_string(path)}' doesn't contain static items {missing_static} - They are readonly - since they are defined via a .nix file"
        raise ClanError(msg)


def validate_not_readonly(path: PathTuple, writeables: AttributeMap) -> None:
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
