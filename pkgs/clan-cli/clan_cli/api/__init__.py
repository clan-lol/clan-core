import dataclasses
import json
from collections.abc import Callable
from dataclasses import dataclass, fields, is_dataclass
from functools import wraps
from inspect import Parameter, Signature, signature
from pathlib import Path
from types import UnionType
from typing import (
    Annotated,
    Any,
    Generic,
    Literal,
    TypeVar,
    get_args,
    get_origin,
    get_type_hints,
)

from clan_cli.errors import ClanError


def sanitize_string(s: str) -> str:
    # Using the native string sanitizer to handle all edge cases
    # Remove the outer quotes '"string"'
    return json.dumps(s)[1:-1]


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
        return sanitize_string(str(obj))
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


T = TypeVar("T")

ResponseDataType = TypeVar("ResponseDataType")


@dataclass
class ApiError:
    message: str
    description: str | None
    location: list[str] | None


@dataclass
class SuccessDataClass(Generic[ResponseDataType]):
    op_key: str
    status: Annotated[Literal["success"], "The status of the response."]
    data: ResponseDataType


@dataclass
class ErrorDataClass:
    op_key: str
    status: Literal["error"]
    errors: list[ApiError]


ApiResponse = SuccessDataClass[ResponseDataType] | ErrorDataClass


def update_wrapper_signature(wrapper: Callable, wrapped: Callable) -> None:
    sig = signature(wrapped)
    params = list(sig.parameters.values())

    # Add 'op_key' parameter
    op_key_param = Parameter(
        "op_key", Parameter.KEYWORD_ONLY, default=None, annotation=str
    )
    params.append(op_key_param)

    # Create a new signature
    new_sig = sig.replace(parameters=params)
    wrapper.__signature__ = new_sig  # type: ignore


class MethodRegistry:
    def __init__(self) -> None:
        self._orig_signature: dict[str, Signature] = {}
        self._registry: dict[str, Callable[..., Any]] = {}

    @property
    def orig_signatures(self) -> dict[str, Signature]:
        return self._orig_signature

    @property
    def signatures(self) -> dict[str, Signature]:
        return {name: signature(fn) for name, fn in self.functions.items()}

    @property
    def functions(self) -> dict[str, Callable[..., Any]]:
        return self._registry

    def reset(self) -> None:
        self._orig_signature.clear()
        self._registry.clear()

    def register_abstract(self, fn: Callable[..., T]) -> Callable[..., T]:
        @wraps(fn)
        def wrapper(*args: Any, op_key: str, **kwargs: Any) -> ApiResponse[T]:
            raise NotImplementedError(
                f"""{fn.__name__} - The platform didn't implement this function.

---
# Example

The function 'open_file()' depends on the platform.

def open_file(file_request: FileRequest) -> str | None:
    # In GTK we open a file dialog window
    # In Android we open a file picker dialog
    # and so on.
    pass

# At runtime the clan-app must override platform specific functions
API.register(open_file)
---
                """
            )

        self.register(wrapper)
        return fn

    def register(self, fn: Callable[..., T]) -> Callable[..., T]:
        if fn.__name__ in self._registry:
            raise ValueError(f"Function {fn.__name__} already registered")
        if fn.__name__ in self._orig_signature:
            raise ValueError(f"Function {fn.__name__} already registered")
        # make copy of original function
        self._orig_signature[fn.__name__] = signature(fn)

        @wraps(fn)
        def wrapper(*args: Any, op_key: str, **kwargs: Any) -> ApiResponse[T]:
            try:
                data: T = fn(*args, **kwargs)
                return SuccessDataClass(status="success", data=data, op_key=op_key)
            except ClanError as e:
                return ErrorDataClass(
                    op_key=op_key,
                    status="error",
                    errors=[
                        ApiError(
                            message=e.msg,
                            description=e.description,
                            location=[fn.__name__, e.location],
                        )
                    ],
                )

        # @wraps preserves all metadata of fn
        # we need to update the annotation, because our wrapper changes the return type
        # This overrides the new return type annotation with the generic typeVar filled in
        orig_return_type = get_type_hints(fn).get("return")
        wrapper.__annotations__["return"] = ApiResponse[orig_return_type]  # type: ignore

        # Add additional argument for the operation key
        wrapper.__annotations__["op_key"] = str  # type: ignore

        update_wrapper_signature(wrapper, fn)

        self._registry[fn.__name__] = wrapper

        return fn

    def to_json_schema(self) -> dict[str, Any]:
        from typing import get_type_hints

        from clan_cli.api.util import type_to_dict

        api_schema: dict[str, Any] = {
            "$comment": "An object containing API methods. ",
            "type": "object",
            "additionalProperties": False,
            "required": [func_name for func_name in self._registry.keys()],
            "properties": {},
        }

        for name, func in self._registry.items():
            hints = get_type_hints(func)

            serialized_hints = {
                key: type_to_dict(
                    value, scope=name + " argument" if key != "return" else "return"
                )
                for key, value in hints.items()
            }

            return_type = serialized_hints.pop("return")

            sig = signature(func)
            required_args = []
            for n, param in sig.parameters.items():
                if param.default == Parameter.empty:
                    required_args.append(n)

            api_schema["properties"][name] = {
                "type": "object",
                "required": ["arguments", "return"],
                "additionalProperties": False,
                "properties": {
                    "return": return_type,
                    "arguments": {
                        "type": "object",
                        "required": required_args,
                        "additionalProperties": False,
                        "properties": serialized_hints,
                    },
                },
            }

        return api_schema

    def get_method_argtype(self, method_name: str, arg_name: str) -> Any:
        from inspect import signature

        func = self._registry.get(method_name, None)
        if func:
            sig = signature(func)
            param = sig.parameters.get(arg_name)
            if param:
                param_class = param.annotation
                return param_class

        return None


API = MethodRegistry()
