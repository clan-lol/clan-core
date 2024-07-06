from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from inspect import Parameter, signature
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
    op_key: str | None


@dataclass
class ErrorDataClass:
    status: Literal["error"]
    errors: list[ApiError]
    op_key: str | None


ApiResponse = SuccessDataClass[ResponseDataType] | ErrorDataClass


def update_wrapper_signature(wrapper: Callable, wrapped: Callable) -> None:
    sig = signature(wrapped)
    params = list(sig.parameters.values())

    # Add 'op_key' parameter
    op_key_param = Parameter(
        "op_key", Parameter.KEYWORD_ONLY, default=None, annotation=str | None
    )
    params.append(op_key_param)

    # Create a new signature
    new_sig = sig.replace(parameters=params)
    wrapper.__signature__ = new_sig  # type: ignore


class _MethodRegistry:
    def __init__(self) -> None:
        self._orig: dict[str, Callable[[Any], Any]] = {}
        self._registry: dict[str, Callable[[Any], Any]] = {}

    def register_abstract(self, fn: Callable[..., T]) -> Callable[..., T]:
        @wraps(fn)
        def wrapper(
            *args: Any, op_key: str | None = None, **kwargs: Any
        ) -> ApiResponse[T]:
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
        self._orig[fn.__name__] = fn

        @wraps(fn)
        def wrapper(
            *args: Any, op_key: str | None = None, **kwargs: Any
        ) -> ApiResponse[T]:
            try:
                data: T = fn(*args, **kwargs)
                return SuccessDataClass(status="success", data=data, op_key=op_key)
            except ClanError as e:
                return ErrorDataClass(
                    status="error",
                    op_key=op_key,
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
        wrapper.__annotations__["op_key"] = str | None  # type: ignore

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


API = _MethodRegistry()
