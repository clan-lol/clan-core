from dataclasses import dataclass, field
from typing import Any, NotRequired, Required

import pytest

from .type_to_jsonschema import JSchemaTypeError, type_to_dict


def test_simple_primitives() -> None:
    assert type_to_dict(int) == {
        "type": "integer",
    }
    assert type_to_dict(float) == {
        "type": "number",
    }

    assert type_to_dict(str) == {
        "type": "string",
    }

    assert type_to_dict(bool) == {
        "type": "boolean",
    }
    assert type_to_dict(object) == {
        "type": "object",
    }


def test_enum_type() -> None:
    from enum import Enum

    class Color(Enum):
        RED = "red"
        GREEN = "green"
        BLUE = "blue"

    assert type_to_dict(Color) == {
        "type": "string",
        "enum": ["red", "green", "blue"],
    }


def test_unsupported_any_types() -> None:
    with pytest.raises(JSchemaTypeError) as exc_info:
        type_to_dict(Any)
    assert "Usage of the Any type is not supported" in str(exc_info.value)

    with pytest.raises(JSchemaTypeError) as exc_info:
        type_to_dict(list[Any])
    assert "Usage of the Any type is not supported" in str(exc_info.value)

    # TBD.
    # with pytest.raises(JSchemaTypeError) as exc_info:
    #     type_to_dict(dict[str, Any])
    # assert "Usage of the Any type is not supported" in str(exc_info.value)

    with pytest.raises(JSchemaTypeError) as exc_info:
        type_to_dict(tuple[Any, ...])
    assert "Usage of the Any type is not supported" in str(exc_info.value)

    with pytest.raises(JSchemaTypeError) as exc_info:
        type_to_dict(set[Any])
    assert "Usage of the Any type is not supported" in str(exc_info.value)

    with pytest.raises(JSchemaTypeError) as exc_info:
        type_to_dict(str | Any)
    assert "Usage of the Any type is not supported" in str(exc_info.value)


def test_allowed_any_types() -> None:
    # Object with arbitrary keys
    assert type_to_dict(dict[str, Any]) == {
        "type": "object",
        "additionalProperties": True,
    }

    # Union where Any is discarded
    assert type_to_dict(str | Any, narrow_unsupported_union_types=True) == {
        "type": "string",
    }


def test_simple_union_types() -> None:
    assert type_to_dict(int | str) == {
        "oneOf": [
            {"type": "integer"},
            {"type": "string"},
        ]
    }

    assert type_to_dict(int | str | float) == {
        "oneOf": [
            {"type": "integer"},
            {"type": "string"},
            {"type": "number"},
        ]
    }

    assert type_to_dict(int | str | None) == {
        "oneOf": [
            {"type": "integer"},
            {"type": "string"},
            {"type": "null"},
        ]
    }


def test_complex_union_types() -> None:
    @dataclass
    class Foo:
        foo: str

    @dataclass
    class Bar:
        bar: str

    assert type_to_dict(Foo | Bar | None) == {
        "oneOf": [
            {
                "type": "object",
                "properties": {
                    "foo": {"type": "string"},
                },
                "additionalProperties": False,
                "required": ["foo"],
            },
            {
                "type": "object",
                "properties": {
                    "bar": {"type": "string"},
                },
                "additionalProperties": False,
                "required": ["bar"],
            },
            {"type": "null"},
        ]
    }


def test_dataclasses() -> None:
    # @dataclass
    # class Example:
    #     name: str
    #     value: bool

    # assert type_to_dict(Example) == {
    #     "type": "object",
    #     "properties": {
    #         "name": {"type": "string"},
    #         "value": {"type": "boolean"},
    #     },
    #     "additionalProperties": False,
    #     "required": [
    #         "name",
    #         "value",
    #     ],
    # }

    @dataclass
    class ExampleWithNullable:
        name: str
        value: int | None

    assert type_to_dict(ExampleWithNullable) == {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {"oneOf": [{"type": "integer"}, {"type": "null"}]},
        },
        "additionalProperties": False,
        "required": [
            "name",
            "value",
        ],  # value is required because it has no default value
    }

    @dataclass
    class ExampleWithOptional:
        name: str
        value: int | None = None

    assert type_to_dict(ExampleWithOptional) == {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {"oneOf": [{"type": "integer"}, {"type": "null"}]},
        },
        "additionalProperties": False,
        "required": [
            "name"
        ],  # value is optional because it has a default value of None
    }


def test_dataclass_with_optional_fields() -> None:
    @dataclass
    class Example:
        value: dict[str, Any] = field(default_factory=dict)

    assert type_to_dict(Example) == {
        "type": "object",
        "properties": {
            "value": {
                "type": "object",
                "additionalProperties": True,
            },
        },
        "additionalProperties": False,
        "required": [],  # value is optional because it has default factory
    }


def test_nested_open_dicts() -> None:
    assert type_to_dict(dict[str, dict[str, list[str]]]) == {
        "type": "object",
        "additionalProperties": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {"type": "string"},
            },
        },
    }


def test_type_variables() -> None:
    from typing import Generic, TypeVar

    T = TypeVar("T")

    @dataclass
    class Wrapper(Generic[T]):
        value: T

    assert type_to_dict(Wrapper[int]) == {
        "type": "object",
        "properties": {
            "value": {"type": "integer"},
        },
        "additionalProperties": False,
        "required": ["value"],
    }

    assert type_to_dict(Wrapper[str]) == {
        "type": "object",
        "properties": {
            "value": {"type": "string"},
        },
        "additionalProperties": False,
        "required": ["value"],
    }


def test_type_variable_nested_scopes() -> None:
    # Define two type variables with the same name "T" but in different scopes

    from typing import Generic, TypeVar

    T = TypeVar("T")

    @dataclass
    class Outer(Generic[T]):
        foo: T

    @dataclass
    class Inner(Generic[T]):
        bar: T

    assert type_to_dict(Outer[Inner[int]]) == {
        "type": "object",
        "properties": {
            "foo": {
                "type": "object",
                "properties": {
                    "bar": {"type": "integer"},
                },
                "additionalProperties": False,
                "required": ["bar"],
            },
        },
        "additionalProperties": False,
        "required": ["foo"],
    }


def test_total_typed_dict() -> None:
    from typing import TypedDict

    class ExampleTypedDict(TypedDict):
        name: str
        value: NotRequired[int]
        bar: int | None

    assert type_to_dict(ExampleTypedDict) == {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {"type": "integer"},
            "bar": {
                "oneOf": [
                    {
                        "type": "integer",
                    },
                    {
                        "type": "null",
                    },
                ],
            },
        },
        "additionalProperties": False,
        # bar is required because it's not explicitly marked as 'NotRequired'
        "required": ["bar", "name"],
    }


def test_open_typed_dict() -> None:
    from typing import TypedDict

    class ExampleTypedDict(TypedDict, total=False):
        name: Required[str]
        value: int

    assert type_to_dict(ExampleTypedDict) == {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {"type": "integer"},
        },
        "additionalProperties": False,
        "required": ["name"],
    }
