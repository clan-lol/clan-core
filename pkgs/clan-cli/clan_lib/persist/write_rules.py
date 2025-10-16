from enum import Enum
from typing import Any

from clan_lib.errors import ClanError
from clan_lib.persist.path_utils import PathTuple, path_to_string

WRITABLE_PRIORITY_THRESHOLD = 100  # Values below this are not writeable


class PersistenceAttribute(Enum):
    WRITE = "write"
    READONLY = "readonly"
    DELETE = "delete"  # can be deleted


type AttributeMap = dict[PathTuple, set[PersistenceAttribute]]


def is_writeable_path(
    key: PathTuple,
    attributes: AttributeMap,
) -> bool:
    """Recursively check if a key is writeable.

    If key "machines.machine1.deploy.targetHost" is specified but writeability is only
    defined for "machines", we pop the last key and check if the parent key is writeable/non-writeable.
    """
    remaining = key
    while remaining:
        current_path = remaining
        if current_path in attributes:
            if PersistenceAttribute.WRITE in attributes[current_path]:
                return True
            if PersistenceAttribute.READONLY in attributes[current_path]:
                return False
        # Check the parent path
        remaining = remaining[:-1]

    msg = f"Cannot determine writeability for key '{key}'"
    raise ClanError(msg)


def is_writeable_key(
    key: str,
    attributes: AttributeMap,
) -> bool:
    """Recursively check if a key is writeable.

    Key is a dot-separated string, e.g. "machines.machine1.deploy.targetHost".

    In case of ambiguity use is_writeable_path with tuple keys.
    """
    items = key.split(".")
    return is_writeable_path(tuple(items), attributes)


def get_priority(value: Any) -> int | None:
    """Extract priority from a value, handling both dict and non-dict cases."""
    if isinstance(value, dict) and "__prio" in value:
        return value["__prio"]
    if isinstance(value, dict) and "__this" in value:
        return value["__this"]["prio"]
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


def get_inventory_exclusive(value: dict, inventory_file_name: str) -> bool | None:
    if "__this" not in value:
        return None

    definition_locations = value.get("__this", {}).get("files")
    if not definition_locations:
        return None

    return (
        len(definition_locations) == 1
        and definition_locations[0] == inventory_file_name
    )


def get_totality(value: dict) -> bool:
    if "__this" not in value:
        return False
    return value.get("__this", {}).get("total", False)


def _determine_props_recursive(
    priorities: dict[str, Any],
    all_values: dict[str, Any],
    persisted: dict[str, Any],
    current_path: PathTuple = (),
    inherited_priority: int | None = None,
    parent_redonly: bool = False,
    results: AttributeMap | None = None,
    parent_total: bool = True,
    *,
    inventory_file_name: str,
) -> AttributeMap:
    """Recursively determine writeability for all paths in the priority structure.

    This is internal recursive function. Use 'determine_writeability' as entry point.

    results: AttributeMap that accumulates results, returned at the end.
    """
    if results is None:
        results = {}

    if not isinstance(all_values, dict):
        # Nothing to do for non-dict values
        # they are handled at parent level
        return results

    for key in all_values:
        value = priorities.get(key, {})

        # Skip metadata keys
        # if key in {"__this", "__list", "__prio"}:
        #     continue

        path = (*current_path, key)

        # If the value is defined only in inventory.json, we might be able to delete it.
        # If we don't know (None), decide to allow deletion as well. (Backwards compatibility)
        # Unless there is a default that applies instead, when removed. Currently we cannot test that.
        # So we assume exclusive values can be removed. In reality we might need to check defaults too. (TODO)
        # Total parents prevent deletion of immediate children.
        is_inventory_exclusive = get_inventory_exclusive(value, inventory_file_name)
        if not parent_total and (
            is_inventory_exclusive or is_inventory_exclusive is None
        ):
            results.setdefault(path, set()).add(PersistenceAttribute.DELETE)
        # Determine priority for this key
        key_priority = get_priority(value)
        effective_priority = (
            key_priority if key_priority is not None else inherited_priority
        )

        # Check if this should be non-writeable due to inheritance
        force_non_writeable = should_inherit_non_writeable(
            effective_priority, parent_redonly
        )

        if force_non_writeable:
            results.setdefault(path, set()).clear()
            results.setdefault(path, set()).add(PersistenceAttribute.READONLY)
            # All children are also non-writeable, we are done here.
            if isinstance(value, dict):
                _determine_props_recursive(
                    value,
                    all_values.get(key, {}),
                    {},  # Doesn't matter since all children will be non-writeable
                    path,
                    effective_priority,
                    parent_redonly=True,
                    results=results,
                    parent_total=get_totality(value),
                    inventory_file_name=inventory_file_name,
                )
        else:
            # Determine writeability based on rules
            if effective_priority is None:
                msg = f"Priority for path '{path_to_string(path)}' is not defined. Cannot determine writeability."
                raise ClanError(msg)

            exists_in_persisted = key in persisted
            value_in_all = all_values.get(key)

            if is_key_writeable(effective_priority, exists_in_persisted, value_in_all):
                # TODO: Distinguish between different write types?
                results.setdefault(path, set()).add(PersistenceAttribute.WRITE)
            else:
                results.setdefault(path, set()).clear()
                results.setdefault(path, set()).add(PersistenceAttribute.READONLY)

            # Recurse into children
            # TODO: Dont need to recurse?
            # if the current value is READONLY all children are readonly as well
            if isinstance(value, dict):
                _determine_props_recursive(
                    value,
                    all_values.get(key, {}),
                    persisted.get(key, {}),
                    path,
                    effective_priority,
                    parent_redonly=False,
                    results=results,
                    parent_total=get_totality(value),
                    inventory_file_name=inventory_file_name,
                )

    return results


def compute_attribute_persistence(
    priorities: dict[str, Any],
    all_values: dict[str, Any],
    persisted: dict[str, Any],
    *,
    inventory_file_name: str = "inventory.json",
) -> AttributeMap:
    """Determine writeability for all paths based on priorities and current data.

    - Priority-based writeability: Values with priority < 100 are not writeable
    - Inheritance: Children inherit parent priorities if not specified
    - Special case at priority 100: Can be writeable if it's mergeable (dict/list) or exists in persisted data

    Args:
        priorities: The priority structure defining writeability rules. See: 'clanInternals.inventoryClass.introspection'
        all_values: All values in the inventory, See: 'clanInternals.inventoryClass.allValues'
        persisted: The current mutable state of the inventory, see: 'readFile inventory.json'
        inventory_file_name: The name of the inventory file, defaults to "inventory.json"

    Returns:
        Dict with sets of writeable and non-writeable paths using tuple keys

    """
    persistence_unsupported = set(all_values.keys()) - set(priorities.keys())
    if persistence_unsupported:
        msg = (
            f"Persistence priorities are not defined for top-level keys: "
            f"{', '.join(sorted(persistence_unsupported))}. "
            f"Either remove them from the python inventory model or extend support of"
            f" persistence properties in 'clanInternals.inventoryClass.introspection'."
        )
        raise ClanError(msg)

    return _determine_props_recursive(
        priorities, all_values, persisted, inventory_file_name=inventory_file_name
    )
