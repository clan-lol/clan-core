import dataclasses
import json
from dataclasses import fields, is_dataclass
from pathlib import Path
from types import UnionType
from typing import Any, get_args, get_origin

from clan_cli.errors import ClanError
from clan_cli.git import commit_file

from .classes import (
    Inventory,
    Machine,
    MachineDeploy,
    Meta,
    Service,
    ServiceBorgbackup,
    ServiceBorgbackupMeta,
    ServiceBorgbackupRole,
    ServiceBorgbackupRoleClient,
    ServiceBorgbackupRoleServer,
)

# Re export classes here
# This allows to rename classes in the generated code
__all__ = [
    "Service",
    "Machine",
    "Meta",
    "Inventory",
    "MachineDeploy",
    "ServiceBorgbackup",
    "ServiceBorgbackupMeta",
    "ServiceBorgbackupRole",
    "ServiceBorgbackupRoleClient",
    "ServiceBorgbackupRoleServer",
]


def sanitize_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def dataclass_to_dict(obj: Any) -> Any:
    """
    Utility function to convert dataclasses to dictionaries
    It converts all nested dataclasses, lists, tuples, and dictionaries to dictionaries

    It does NOT convert member functions.
    """
    if is_dataclass(obj):
        return {
            # Use either the original name or name
            sanitize_string(
                field.metadata.get("original_name", field.name)
            ): dataclass_to_dict(getattr(obj, field.name))
            for field in fields(obj)  # type: ignore
        }
    elif isinstance(obj, list | tuple):
        return [dataclass_to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {sanitize_string(k): dataclass_to_dict(v) for k, v in obj.items()}
    elif isinstance(obj, Path):
        return str(obj)
    elif isinstance(obj, str):
        return sanitize_string(obj)
    else:
        return obj


def is_union_type(type_hint: type) -> bool:
    return type(type_hint) is UnionType


def get_inner_type(type_hint: type) -> type:
    if is_union_type(type_hint):
        # Return the first non-None type
        return next(t for t in get_args(type_hint) if t is not type(None))
    return type_hint


def get_second_type(type_hint: type[dict]) -> type:
    """
    Get the value type of a dictionary type hint
    """
    args = get_args(type_hint)
    if len(args) == 2:
        # Return the second argument, which should be the value type (Machine)
        return args[1]

    raise ValueError(f"Invalid type hint for dict: {type_hint}")


def from_dict(t: type, data: dict[str, Any] | None) -> Any:
    """
    Dynamically instantiate a data class from a dictionary, handling nested data classes.
    """
    if data is None:
        return None

    try:
        # Attempt to create an instance of the data_class
        field_values = {}
        for field in fields(t):
            original_name = field.metadata.get("original_name", field.name)

            field_value = data.get(original_name)

            field_type = get_inner_type(field.type)  # type: ignore

            if original_name in data:
                # If the field is another dataclass, recursively instantiate it
                if is_dataclass(field_type):
                    field_value = from_dict(field_type, field_value)
                elif isinstance(field_type, Path | str) and isinstance(
                    field_value, str
                ):
                    field_value = (
                        Path(field_value) if field_type == Path else field_value
                    )
                elif get_origin(field_type) is dict and isinstance(field_value, dict):
                    # The field is a dictionary with a specific type
                    inner_type = get_second_type(field_type)
                    field_value = {
                        k: from_dict(inner_type, v) for k, v in field_value.items()
                    }
                elif get_origin is list and isinstance(field_value, list):
                    # The field is a list with a specific type
                    inner_type = get_args(field_type)[0]
                    field_value = [from_dict(inner_type, v) for v in field_value]

            # Set the value
            if (
                field.default is not dataclasses.MISSING
                or field.default_factory is not dataclasses.MISSING
            ):
                # Fields with default value
                # a: Int = 1
                # b: list = Field(default_factory=list)
                if original_name in data or field_value is not None:
                    field_values[field.name] = field_value
            else:
                # Fields without default value
                # a: Int
                field_values[field.name] = field_value

        return t(**field_values)

    except (TypeError, ValueError) as e:
        print(f"Failed to instantiate {t.__name__}: {e} {data}")
        return None
        # raise ClanError(f"Failed to instantiate {t.__name__}: {e}")


def get_path(flake_dir: str | Path) -> Path:
    """
    Get the path to the inventory file in the flake directory
    """
    return (Path(flake_dir) / "inventory.json").resolve()


# Default inventory
default_inventory = Inventory(
    meta=Meta(name="New Clan"), machines={}, services=Service()
)


def load_inventory(
    flake_dir: str | Path, default: Inventory = default_inventory
) -> Inventory:
    """
    Load the inventory file from the flake directory
    If not file is found, returns the default inventory
    """
    inventory = default_inventory

    inventory_file = get_path(flake_dir)
    if inventory_file.exists():
        with open(inventory_file) as f:
            try:
                res = json.load(f)
                inventory = from_dict(Inventory, res)
            except json.JSONDecodeError as e:
                # Error decoding the inventory file
                raise ClanError(f"Error decoding inventory file: {e}")

    return inventory


def save_inventory(inventory: Inventory, flake_dir: str | Path, message: str) -> None:
    """ "
    Write the inventory to the flake directory
    and commit it to git with the given message
    """
    inventory_file = get_path(flake_dir)

    with open(inventory_file, "w") as f:
        json.dump(dataclass_to_dict(inventory), f, indent=2)

    commit_file(inventory_file, Path(flake_dir), commit_message=message)
