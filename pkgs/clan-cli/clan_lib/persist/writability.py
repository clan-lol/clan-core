from typing import Any, TypedDict

from clan_lib.errors import ClanError
from clan_lib.persist.path_utils import PathTuple, path_to_string

WRITABLE_PRIORITY_THRESHOLD = 100  # Values below this are not writeable


class WriteabilityResult(TypedDict):
    writeable: set[PathTuple]
    non_writeable: set[PathTuple]


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


def is_writeable_key(
    key: str,
    writeables: WriteabilityResult,
) -> bool:
    """Recursively check if a key is writeable.

    Key is a dot-separated string, e.g. "machines.machine1.deploy.targetHost".

    In case of ambiguity use is_writeable_path with tuple keys.
    """
    items = key.split(".")
    return is_writeable_path(tuple(items), writeables)


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
