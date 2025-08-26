"""Provides utility functions for serialization and deserialization of data classes.

Functions:
- sanitize_string(s: str) -> str: Ensures a string is properly escaped for json serializing.
- dataclass_to_dict(obj: Any) -> Any: Converts a data class and its nested data classes, lists, tuples, and dictionaries to dictionaries.
- from_dict(t: type[T], data: Any) -> T: Dynamically instantiates a data class from a dictionary, constructing nested data classes, validates all required fields exist and have the expected type.

Classes:
- TypeAdapter: A Pydantic type adapter for data classes.

Exceptions:
- ValidationError: Raised when there is a validation error during deserialization.
- ClanError: Raised when there is an error during serialization or deserialization.

Dependencies:
- dataclasses: Provides the @dataclass decorator and related functions for creating data classes.
- json: Provides functions for working with JSON data.
- collections.abc: Provides abstract base classes for collections.
- functools: Provides functions for working with higher-order functions and decorators.
- inspect: Provides functions for inspecting live objects.
- operator: Provides functions for working with operators.
- pathlib: Provides classes for working with filesystem paths.
- types: Provides functions for working with types.
- typing: Provides support for type hints.
- pydantic: A library for data validation and settings management.
- pydantic_core: Core functionality for Pydantic.

Note: This module assumes the presence of other modules and classes such as `ClanError` and `ErrorDetails` from the `clan_lib.errors` module.
"""

import dataclasses
import inspect
import traceback
from dataclasses import dataclass, fields, is_dataclass
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import (
    Annotated,
    Any,
    Literal,
    TypeVar,
    Union,
    cast,
    get_args,
    get_origin,
    is_typeddict,
)

from clan_lib.errors import ClanError


def sanitize_string(s: str) -> str:
    # Currently, this is a no-op
    # but it can be extended to escape special characters if we need it
    return s


def is_enum(obj: Any) -> bool:
    """Safely checks if the object or one of its attributes is an Enum."""
    # Check if the object itself is an Enum
    if isinstance(obj, Enum):
        return True

    # Check if the object has an 'enum' attribute and if it's an Enum
    enum_attr = getattr(obj, "enum", None)
    return isinstance(enum_attr, Enum)


def get_enum_value(obj: Any) -> Any:
    """Safely checks if the object or one of its attributes is an Enum."""
    # Check if the object itself is an Enum
    value = getattr(obj, "value", None)
    if value is None and obj.enum:
        value = getattr(obj.enum, "value", None)

    if value is None:
        error_msg = f"Cannot determine enum value for {obj}"
        raise ValueError(error_msg)

    return dataclass_to_dict(value)


def dataclass_to_dict(obj: Any, *, use_alias: bool = True) -> Any:
    """Converts objects to dictionaries.

    This function is round trip safe.
    Meaning that if you convert the object to a dict and then back to a dataclass using 'from_dict'

    List of supported types:
    - dataclass
    - list
    - tuple
    - set
    - dict
    - Path: Gets converted to string
    - Enum: Gets converted to its value

    """

    def _to_dict(obj: Any) -> Any:
        """Utility function to convert dataclasses to dictionaries
        It converts all nested dataclasses, lists, tuples, and dictionaries to dictionaries

        It does NOT convert member functions.
        """
        if is_enum(obj):
            return get_enum_value(obj)
        if is_dataclass(obj):
            return {
                # Use either the original name or name
                sanitize_string(
                    field.metadata.get("alias", field.name)
                    if use_alias
                    else field.name,
                ): _to_dict(getattr(obj, field.name))
                for field in fields(obj)
                if not field.name.startswith("_")
                and getattr(obj, field.name) is not None  # type: ignore[no-any-return]
            }
        if isinstance(obj, list | tuple | set):
            return [_to_dict(item) for item in obj]
        if isinstance(obj, dict):
            return {sanitize_string(k): _to_dict(v) for k, v in obj.items()}
        if isinstance(obj, Path):
            return sanitize_string(str(obj))
        if isinstance(obj, str):
            return sanitize_string(obj)
        return obj

    return _to_dict(obj)


T = TypeVar("T", bound=dataclass)  # type: ignore[valid-type]


def is_union_type(type_hint: type | UnionType) -> bool:
    return (
        type(type_hint) is UnionType
        or isinstance(type_hint, UnionType)
        or get_origin(type_hint) is Union
    )


def is_type_in_union(union_type: type | UnionType, target_type: type) -> bool:
    # Check for Union from typing module (Union[str, None]) or UnionType (str | None)
    if get_origin(union_type) in (Union, UnionType):
        args = get_args(union_type)
        for arg in args:
            # Handle None type specially since it's not a class
            if arg is None or arg is type(None):
                if target_type is type(None):
                    return True
            # For generic types like dict[str, str], check their origin
            elif get_origin(arg) is not None:
                if get_origin(arg) == target_type or (
                    get_origin(target_type) is not None
                    and get_origin(arg) == get_origin(target_type)
                ):
                    return True
            # For actual classes, use issubclass
            elif inspect.isclass(arg) and inspect.isclass(target_type):
                if issubclass(arg, target_type):
                    return True
            # For non-class types, use direct comparison
            elif arg == target_type:
                return True
        return False
    return union_type == target_type


def unwrap_none_type(type_hint: type | UnionType) -> type:
    """Takes a type union and returns the first non-None type.
    None | str
    =>
    str
    """
    if is_union_type(type_hint):
        # Return the first non-None type
        return next(t for t in get_args(type_hint) if t is not type(None))

    return type_hint  # type: ignore[return-value]


def unwrap_union_type(type_hint: type | UnionType) -> list[type]:
    """Takes a type union and returns the first non-None type.
    None | str
    =>
    str
    """
    if is_union_type(type_hint):
        # Return the first non-None type
        return list(get_args(type_hint))

    return [type_hint]  # type: ignore[list-item]


JsonValue = str | float | dict[str, Any] | list[Any] | None


def construct_value(
    t: type | UnionType,
    field_value: JsonValue,
    loc: list[str] | None = None,
) -> Any:
    """Construct a field value from a type hint and a field value.

    The following types are supported and matched in this order:

    - None
    - dataclass
    - Path: Constructed from a string, Error if value is not string
    - dict
    - str
    - int, float: Constructed from any value, Error if value is string
    - bool: Constructed from any value, Error if value is not boolean
    - Union: Construct the value of the first non-None type. Example: 'None | Path | str' -> Path
    - list: Construct Members recursively from inner type of the list. Error if value not a list
    - dict: Construct Members recursively from inner type of the dict. Error if value not a dict
    - Literal: Check if the value is one of the valid values. Error if value not in valid values
    - Enum: Construct the Enum by passing the value into the enum constructor. Error is Enum cannot be constructed
    - Annotated: Unwrap the type and construct the value
    - TypedDict: Construct the TypedDict by passing the value into the TypedDict constructor. Error if value not a dict
    - Unknown: Return the field value as is, type reserved 'class Unknown'

    - Otherwise: Raise a ClanError
    """
    if loc is None:
        loc = []
    if t is None and field_value:
        msg = f"Trying to construct field of type None. But got: {field_value}. loc: {loc}"
        raise ClanError(msg, location=f"{loc}")

    if is_type_in_union(t, type(None)) and field_value is None:
        # Sometimes the field value is None, which is valid if the type hint allows None
        return None

    # If the field is another dataclass
    # Field_value must be a dictionary
    if is_dataclass(t) and isinstance(field_value, dict):
        if not isinstance(t, type):
            msg = f"Expected a type, got {t}"
            raise ClanError(msg)
        return construct_dataclass(t, field_value)

    # If the field expects a path
    # Field_value must be a string
    if is_type_in_union(t, Path):
        if not isinstance(field_value, str):
            msg = (
                f"Expected string, cannot construct pathlib.Path() from: {field_value} "
            )
            raise ClanError(
                msg,
                location=f"{loc}",
            )

        return Path(field_value)

    if t is str:
        if not isinstance(field_value, str):
            msg = f"Expected string, got {field_value}"
            raise ClanError(msg, location=f"{loc}")

        return field_value

    if t is int and not isinstance(field_value, str):
        return int(field_value)  # type: ignore[arg-type]
    if t is float and not isinstance(field_value, str):
        return float(field_value)  # type: ignore[arg-type]
    if t is bool and isinstance(field_value, bool):
        return field_value  # type: ignore[misc]

    # Union types construct the first non-None type
    if is_union_type(t):
        # Unwrap the union type
        inner_types = unwrap_union_type(t)
        # Construct the field value
        errors = []
        for inner_type in inner_types:
            try:
                return construct_value(inner_type, field_value, loc)
            except ClanError as exc:
                errors.append(exc)
                continue
        msg = f"Cannot construct field of type {t} while constructing a union type from value: {field_value}"
        for e in errors:
            traceback.print_exception(e)
        raise ClanError(msg, location=f"{loc}")

    # Nested types
    # list
    # dict
    origin = get_origin(t)
    if origin is list:
        if not isinstance(field_value, list):
            msg = f"Expected list, got {field_value}"
            raise ClanError(msg, location=f"{loc}")

        return [construct_value(get_args(t)[0], item) for item in field_value]
    if origin is dict and isinstance(field_value, dict):
        return {
            key: construct_value(get_args(t)[1], value)
            for key, value in field_value.items()
        }
    if origin is Literal:
        valid_values = get_args(t)
        if field_value not in valid_values:
            msg = f"Expected one of {', '.join(valid_values)}, got {field_value}"
            raise ClanError(msg, location=f"{loc}")
        return field_value

    # Enums
    if origin is Enum:
        try:
            return t(field_value)  # type: ignore[operator]
        except ValueError:
            msg = f"Expected one of {', '.join(str(origin))}, got {field_value}"
            raise ClanError(msg, location=f"{loc}") from ValueError

    if isinstance(t, type) and issubclass(t, Enum):
        try:
            return t(field_value)  # type: ignore[operator]
        except ValueError:
            msg = f"Expected one of {', '.join(t.__members__)}, got {field_value}"
            raise ClanError(msg, location=f"{loc}") from ValueError

    if origin is Annotated:
        (base_type,) = get_args(t)
        return construct_value(base_type, field_value)

    # elif get_origin(t) is Union:
    if t is Any:
        return field_value

    if is_typeddict(t):
        if not isinstance(field_value, dict):
            msg = f"Expected TypedDict {t}, got {field_value}"
            raise ClanError(msg, location=f"{loc}")

        return t(field_value)  # type: ignore[call-arg,operator]

    if inspect.isclass(t) and t.__name__ == "Unknown":
        # Return the field value as is
        return field_value

    msg = f"Unhandled field type {t} with value {field_value}"
    raise ClanError(msg)


def construct_dataclass[T: Any](
    t: type[T],
    data: dict[str, Any],
    path: list[str] | None = None,
) -> T:
    """Type t MUST be a dataclass
    Dynamically instantiate a data class from a dictionary, handling nested data classes.

    Constructs the field values from the data dictionary using 'construct_value'
    """
    if path is None:
        path = []
    if not is_dataclass(t):
        msg = f"{t.__name__} is not a dataclass"
        raise ClanError(msg)

    # Attempt to create an instance of the data_class#
    field_values: dict[str, Any] = {}
    required: list[str] = []

    for field in fields(t):
        if field.name.startswith("_"):
            continue
        # The first type in a Union
        # str <- None | str | Path
        data_field_name = field.metadata.get("alias", field.name)

        if (
            field.default is dataclasses.MISSING
            and field.default_factory is dataclasses.MISSING
        ):
            required.append(field.name)

        # Populate the field_values dictionary with the field value
        # if present in the data
        if data_field_name in data:
            field_value = data.get(data_field_name)

            if field_value is None and (
                field.type is None or is_type_in_union(field.type, type(None))  # type: ignore[arg-type]
            ):
                field_values[field.name] = None
            else:
                field_values[field.name] = construct_value(
                    cast("type", field.type), field_value
                )

    # Check that all required field are present.
    for field_name in required:
        if field_name not in field_values:
            formatted_path = " ".join(path)
            msg = f"Default value missing for: '{field_name}' in {t} {formatted_path}, got Value: {data}"
            raise ClanError(msg)

    return t(**field_values)  # type: ignore[return-value]


def from_dict(
    t: type | UnionType,
    data: dict[str, Any] | Any,
    path: list[str] | None = None,
) -> Any:
    """Dynamically instantiate a data class from a dictionary, handling nested data classes.

    This function is round trip safe in conjunction with 'dataclass_to_dict'
    """
    if path is None:
        path = []
    if is_dataclass(t):
        if not isinstance(data, dict):
            msg = f"{data} is not a dict. Expected {t}"
            raise ClanError(msg)
        return construct_dataclass(t, data, path)  # type: ignore[misc]
    return construct_value(t, data, path)
