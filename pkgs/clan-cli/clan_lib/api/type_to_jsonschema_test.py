from dataclasses import dataclass, field
from enum import Enum
from typing import Any, ForwardRef, Generic, NotRequired, Required, TypedDict, TypeVar

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
        ],
    }

    assert type_to_dict(int | str | float) == {
        "oneOf": [
            {"type": "integer"},
            {"type": "string"},
            {"type": "number"},
        ],
    }

    assert type_to_dict(int | str | None) == {
        "oneOf": [
            {"type": "integer"},
            {"type": "string"},
            {"type": "null"},
        ],
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
        ],
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
            "name",
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


def test_type_alias() -> None:
    # Test simple type alias
    type UserId = int

    assert type_to_dict(UserId) == {
        "type": "integer",
    }

    # Test union type alias
    type InputName = str | None

    assert type_to_dict(InputName) == {
        "oneOf": [
            {"type": "string"},
            {"type": "null"},
        ],
    }

    # Test complex type alias with list
    type ServiceName = str
    type ServiceNames = list[ServiceName]

    assert type_to_dict(ServiceNames) == {
        "type": "array",
        "items": {"type": "string"},
    }

    # Test type alias in a dataclass field
    type Readme = str | None

    @dataclass
    class ServiceReadmeCollection:
        input_name: str | None
        readmes: dict[str, Readme]

    assert type_to_dict(ServiceReadmeCollection) == {
        "type": "object",
        "properties": {
            "input_name": {
                "oneOf": [
                    {"type": "string"},
                    {"type": "null"},
                ],
            },
            "readmes": {
                "type": "object",
                "additionalProperties": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "null"},
                    ],
                },
            },
        },
        "additionalProperties": False,
        "required": ["input_name", "readmes"],
    }


def test_string_type_annotation_jsonvalue() -> None:
    # Test that "JSONValue" string type annotation returns permissive schema
    result = type_to_dict("JSONValue")
    assert result == {}, "JSONValue should return empty schema allowing any type"


def test_string_type_annotation_error() -> None:
    # Test that other string type annotations raise an error
    with pytest.raises(JSchemaTypeError) as exc_info:
        type_to_dict("SomeUnknownType")
    assert "String type annotation 'SomeUnknownType' cannot be resolved" in str(
        exc_info.value
    )


def test_forwardref_resolution() -> None:
    # Create a ForwardRef that references a built-in type
    forward_ref = ForwardRef("int")
    forward_ref.__forward_module__ = "builtins"

    result = type_to_dict(forward_ref)
    assert result == {"type": "integer"}

    # Test ForwardRef to str
    forward_ref_str = ForwardRef("str")
    forward_ref_str.__forward_module__ = "builtins"

    result_str = type_to_dict(forward_ref_str)
    assert result_str == {"type": "string"}


def test_forwardref_resolution_from_module() -> None:
    # Create a ForwardRef that references a complex type from typing module
    forward_ref = ForwardRef("list[str]")
    forward_ref.__forward_module__ = "builtins"

    # This test verifies that we can resolve complex type expressions
    result = type_to_dict(forward_ref)
    assert result == {"type": "array", "items": {"type": "string"}}


def test_forwardref_without_module() -> None:
    # Test that ForwardRef without module info raises an error
    forward_ref = ForwardRef("SomeType")

    with pytest.raises(JSchemaTypeError) as exc_info:
        type_to_dict(forward_ref)
    assert "ForwardRef without module or type name" in str(exc_info.value)


def test_forwardref_invalid_type() -> None:
    # Test that ForwardRef with invalid type name raises an error
    forward_ref = ForwardRef("NonExistentType")
    forward_ref.__forward_module__ = "builtins"

    with pytest.raises(JSchemaTypeError) as exc_info:
        type_to_dict(forward_ref)
    assert "Could not resolve ForwardRef" in str(exc_info.value)
