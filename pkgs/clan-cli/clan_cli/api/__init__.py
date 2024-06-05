from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Annotated, Any, Generic, Literal, TypeVar, get_type_hints

from clan_cli.errors import ClanError

T = TypeVar("T")

ResponseDataType = TypeVar("ResponseDataType")


@dataclass
class ApiError:
    message: str
    description: str | None
    location: list[str] | None


@dataclass
class SuccessDataClass(Generic[ResponseDataType]):
    status: Annotated[Literal["success"], "The status of the response."]
    data: ResponseDataType


@dataclass
class ErrorDataClass:
    status: Literal["error"]
    errors: list[ApiError]


ApiResponse = SuccessDataClass[ResponseDataType] | ErrorDataClass


class _MethodRegistry:
    def __init__(self) -> None:
        self._orig: dict[str, Callable[[Any], Any]] = {}
        self._registry: dict[str, Callable[[Any], Any]] = {}

    def register(self, fn: Callable[..., T]) -> Callable[..., T]:
        self._orig[fn.__name__] = fn

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> ApiResponse[T]:
            try:
                data: T = fn(*args, **kwargs)
                return SuccessDataClass(status="success", data=data)
            except ClanError as e:
                return ErrorDataClass(
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
