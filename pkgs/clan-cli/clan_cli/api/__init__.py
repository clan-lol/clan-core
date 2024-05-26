from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Generic, Literal, TypeVar

T = TypeVar("T")


ResponseDataType = TypeVar("ResponseDataType")


@dataclass
class ApiError:
    message: str
    description: str | None
    location: list[str] | None


@dataclass
class ApiResponse(Generic[ResponseDataType]):
    status: Literal["success", "error"]
    errors: list[ApiError] | None
    data: ResponseDataType | None


class _MethodRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, Callable[[Any], Any]] = {}

    def register(self, fn: Callable[..., T]) -> Callable[..., T]:
        self._registry[fn.__name__] = fn
        return fn

    def to_json_schema(self) -> dict[str, Any]:
        # Import only when needed
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

            api_schema["properties"][name] = {
                "type": "object",
                "required": ["arguments", "return"],
                "additionalProperties": False,
                "properties": {
                    "return": return_type,
                    "arguments": {
                        "type": "object",
                        "required": [k for k in serialized_hints.keys()],
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


API = _MethodRegistry()
