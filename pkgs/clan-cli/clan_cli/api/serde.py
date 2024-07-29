"""
This module provides utility functions for serialization and deserialization of data classes.

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

Note: This module assumes the presence of other modules and classes such as `ClanError` and `ErrorDetails` from the `clan_cli.errors` module.
"""

import json
from dataclasses import dataclass, fields, is_dataclass
from pathlib import Path
from typing import (
    Any,
    TypeVar,
)

from pydantic import TypeAdapter, ValidationError
from pydantic_core import ErrorDetails

from clan_cli.errors import ClanError


def sanitize_string(s: str) -> str:
    # Using the native string sanitizer to handle all edge cases
    # Remove the outer quotes '"string"'
    return json.dumps(s)[1:-1]


def dataclass_to_dict(obj: Any, *, use_alias: bool = True) -> Any:
    def _to_dict(obj: Any) -> Any:
        """
        Utility function to convert dataclasses to dictionaries
        It converts all nested dataclasses, lists, tuples, and dictionaries to dictionaries

        It does NOT convert member functions.
        """
        if is_dataclass(obj):
            return {
                # Use either the original name or name
                sanitize_string(
                    field.metadata.get("alias", field.name) if use_alias else field.name
                ): _to_dict(getattr(obj, field.name))
                for field in fields(obj)
                if not field.name.startswith("_")  # type: ignore
            }
        elif isinstance(obj, list | tuple):
            return [_to_dict(item) for item in obj]
        elif isinstance(obj, dict):
            return {sanitize_string(k): _to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, Path):
            return sanitize_string(str(obj))
        elif isinstance(obj, str):
            return sanitize_string(obj)
        else:
            return obj

    return _to_dict(obj)


T = TypeVar("T", bound=dataclass)  # type: ignore


def from_dict(t: type[T], data: Any) -> T:
    """
    Dynamically instantiate a data class from a dictionary, handling nested data classes.
    We use dataclasses. But the deserialization logic of pydantic takes a lot of complexity.
    """
    adapter = TypeAdapter(t)
    try:
        return adapter.validate_python(data)
    except ValidationError as e:
        fst_error: ErrorDetails = e.errors()[0]
        if not fst_error:
            raise ClanError(msg=str(e))

        msg = fst_error.get("msg")
        loc = fst_error.get("loc")
        field_path = "Unknown"
        if loc:
            field_path = str(loc)
        raise ClanError(msg=msg, location=f"{t!s}: {field_path}", description=str(e))
