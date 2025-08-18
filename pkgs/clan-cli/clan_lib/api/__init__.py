import importlib
import logging
import pkgutil
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from inspect import Parameter, Signature, signature
from queue import Queue
from types import ModuleType
from typing import (
    Annotated,
    Any,
    Literal,
    TypedDict,
    TypeVar,
    get_type_hints,
)

from clan_lib.api.util import JSchemaTypeError
from clan_lib.async_run import get_current_thread_opkey
from clan_lib.errors import ClanError

from .serde import dataclass_to_dict, from_dict, sanitize_string

log = logging.getLogger(__name__)


__all__ = ["dataclass_to_dict", "from_dict", "sanitize_string"]


T = TypeVar("T")

ResponseDataType = TypeVar("ResponseDataType")


class ProcessMessage(TypedDict):
    """
    Represents a message to be sent to the UI.

    Attributes:
    - topic: The topic of the message, used to identify the type of message.
    - data: The data to be sent with the message.
    - origin: The API operation that this message is related to, if applicable.
    """

    topic: str
    data: Any
    origin: str | None


message_queue: Queue[ProcessMessage] = Queue()
"""
A global message queue for sending messages to the UI
This can be used to send notifications or messages to the UI. Before returning a response.

The clan-app imports the queue as clan_lib.api.message_queue and subscribes to it.
"""


@dataclass
class ApiError:
    message: str
    description: str | None
    location: list[str] | None


@dataclass
class SuccessDataClass[ResponseDataType]:
    op_key: str
    status: Annotated[Literal["success"], "The status of the response."]
    data: ResponseDataType


@dataclass
class ErrorDataClass:
    op_key: str
    status: Literal["error"]
    errors: list[ApiError]


ApiResponse = SuccessDataClass[ResponseDataType] | ErrorDataClass


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
        def wrapper(*args: Any, **kwargs: Any) -> ApiResponse[T]:
            msg = f"""{fn.__name__} - The platform didn't implement this function.

---
# Example

The function 'get_system_file()' depends on the platform.

def get_system_file(file_request: FileRequest) -> str | None:
    # In GTK we open a file dialog window
    # In Android we open a file picker dialog
    # and so on.
    pass

# At runtime the clan-app must override platform specific functions
API.register(get_system_file)
---
                """
            raise NotImplementedError(msg)

        self.register(wrapper)
        return fn

    def overwrite_fn(self, fn: Callable[..., Any]) -> None:
        fn_name = fn.__name__

        if fn_name not in self._registry:
            msg = f"Function '{fn_name}' is not registered as an API method"
            raise ClanError(msg)

        fn_signature = signature(fn)
        abstract_signature = signature(self._registry[fn_name])

        if fn_signature != abstract_signature:
            msg = f"For function: {fn_name}. Expected signature: {abstract_signature}\nActual signature: {fn_signature}"
            raise ClanError(msg)

        self._registry[fn_name] = fn

    F = TypeVar("F", bound=Callable[..., Any])

    def register(self, fn: F) -> F:
        if fn.__name__ in self._registry:
            msg = f"Function {fn.__name__} already registered"
            raise ClanError(msg)
        if fn.__name__ in self._orig_signature:
            msg = f"Function {fn.__name__} already registered"
            raise ClanError(msg)
        # make copy of original function
        self._orig_signature[fn.__name__] = signature(fn)

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> ApiResponse[T]:
            op_key = get_current_thread_opkey()
            if op_key is None:
                msg = f"While executing {fn.__name__}. Middleware forgot to set_current_thread_opkey()"
                raise RuntimeError(msg)
            try:
                data: T = fn(*args, **kwargs)
                return SuccessDataClass(status="success", data=data, op_key=op_key)
            except ClanError as e:
                log.exception(f"Error calling wrapped {fn.__name__}")
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
            except Exception as e:
                log.exception(f"Error calling wrapped {fn.__name__}")
                return ErrorDataClass(
                    op_key=op_key,
                    status="error",
                    errors=[
                        ApiError(
                            message=str(e),
                            description="An unexpected error occurred",
                            location=[fn.__name__],
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

        from .util import type_to_dict

        api_schema: dict[str, Any] = {
            "$comment": "An object containing API methods. ",
            "type": "object",
            "additionalProperties": False,
            "required": list(self._registry.keys()),
            "properties": {},
        }

        err_type = None
        for name, func in self._registry.items():
            hints = get_type_hints(func)

            try:
                serialized_hints = {
                    key: type_to_dict(
                        value,
                        scope=name + " argument" if key != "return" else "return",
                        narrow_unsupported_union_types=True,
                    )
                    for key, value in hints.items()
                }
            except JSchemaTypeError as e:
                msg = f"Error serializing type hints for function '{name}': {e}"
                raise JSchemaTypeError(msg) from e

            return_type = serialized_hints.pop("return")

            if err_type is None:
                err_type = next(
                    t
                    for t in return_type["oneOf"]
                    if ("error" in t["properties"]["status"]["enum"])
                )

            return_type["oneOf"][1] = {"$ref": "#/$defs/error"}

            sig = signature(func)
            required_args = []
            for n, param in sig.parameters.items():
                if param.default == Parameter.empty:
                    required_args.append(n)

            api_schema["properties"][name] = {
                "type": "object",
                "required": ["arguments", "return"],
                "additionalProperties": False,
                "description": func.__doc__,
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

        api_schema["$defs"] = {"error": err_type}

        return api_schema

    def get_method_argtype(self, method_name: str, arg_name: str) -> Any:
        from inspect import signature

        func = self._registry.get(method_name, None)
        if not func:
            msg = f"API Method {method_name} not found in registry. Available methods: {list(self._registry.keys())}"
            raise ClanError(msg)

        sig = signature(func)

        # seems direct 'key in dict' doesnt work here
        if arg_name not in sig.parameters.keys():  # noqa: SIM118
            msg = f"Argument {arg_name} not found in api method '{method_name}'. Available arguments: {list(sig.parameters.keys())}"
            raise ClanError(msg)

        param = sig.parameters.get(arg_name)
        if param:
            param_class = param.annotation
            return param_class

        return None


def import_all_modules_from_package(pkg: ModuleType) -> None:
    for _loader, module_name, _is_pkg in pkgutil.walk_packages(
        pkg.__path__, prefix=f"{pkg.__name__}."
    ):
        base_name = module_name.split(".")[-1]

        # Skip test modules
        if (
            base_name.startswith("test_")
            or base_name.endswith("_test")
            or base_name == "conftest"
        ):
            continue

        importlib.import_module(module_name)


def load_in_all_api_functions() -> None:
    """
    For the global API object, to have all functions available.
    We have to make sure python loads every wrapped function at least once.
    This is done by importing all modules from the clan_lib and clan_cli packages.
    """
    import clan_cli

    import clan_lib

    import_all_modules_from_package(clan_lib)
    import_all_modules_from_package(clan_cli)


API = MethodRegistry()
