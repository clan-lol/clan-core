import dataclasses
import logging
from dataclasses import fields, is_dataclass
from pathlib import Path
from types import UnionType
from typing import Any, get_args

import gi

gi.require_version("WebKit", "6.0")

log = logging.getLogger(__name__)


def sanitize_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def dataclass_to_dict(obj: Any) -> Any:
    """
    Utility function to convert dataclasses to dictionaries
    It converts all nested dataclasses, lists, tuples, and dictionaries to dictionaries

    It does NOT convert member functions.
    """
    if dataclasses.is_dataclass(obj):
        return {
            sanitize_string(k): dataclass_to_dict(v)
            for k, v in dataclasses.asdict(obj).items()
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


def from_dict(t: type, data: dict[str, Any] | None) -> Any:
    """
    Dynamically instantiate a data class from a dictionary, handling nested data classes.
    """
    if not data:
        return None

    try:
        # Attempt to create an instance of the data_class
        field_values = {}
        for field in fields(t):
            field_value = data.get(field.name)
            field_type = get_inner_type(field.type)
            if field_value is not None:
                # If the field is another dataclass, recursively instantiate it
                if is_dataclass(field_type):
                    field_value = from_dict(field_type, field_value)
                elif isinstance(field_type, Path | str) and isinstance(
                    field_value, str
                ):
                    field_value = (
                        Path(field_value) if field_type == Path else field_value
                    )

            if (
                field.default is not dataclasses.MISSING
                or field.default_factory is not dataclasses.MISSING
            ):
                # Field has a default value. We cannot set the value to None
                if field_value is not None:
                    field_values[field.name] = field_value
            else:
                field_values[field.name] = field_value

        return t(**field_values)

    except (TypeError, ValueError) as e:
        print(f"Failed to instantiate {t.__name__}: {e}")
        return None
