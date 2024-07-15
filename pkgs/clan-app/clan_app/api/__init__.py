import logging
from collections.abc import Callable
from typing import Any, ClassVar, Generic, ParamSpec, TypeVar, cast

from gi.repository import GLib, GObject

log = logging.getLogger(__name__)


class GResult(GObject.Object):
    result: Any
    op_key: str
    method_name: str

    def __init__(self, result: Any, method_name: str, op_key: str) -> None:
        super().__init__()
        self.op_key = op_key
        self.result = result
        self.method_name = method_name


B = TypeVar("B")
P = ParamSpec("P")


class ImplFunc(GObject.Object, Generic[P, B]):
    op_key: str | None = None
    __gsignals__: ClassVar = {
        "returns": (GObject.SignalFlags.RUN_FIRST, None, [GResult]),
    }

    def returns(self, result: B) -> None:
        method_name = self.__class__.__name__
        if self.op_key is None:
            raise ValueError(f"op_key is not set for the function {method_name}")
        self.emit("returns", GResult(result, method_name, self.op_key))

    def await_result(self, fn: Callable[["ImplFunc[..., Any]", B], None]) -> None:
        self.connect("returns", fn)

    def async_run(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        raise NotImplementedError("Method 'async_run' must be implemented")

    def _async_run(self, data: Any, op_key: str) -> bool:
        self.op_key = op_key
        result = GLib.SOURCE_REMOVE
        try:
            result = self.async_run(**data)
        except Exception as e:
            log.exception(e)
            # TODO: send error to js
        finally:
            return result


class GObjApi:
    def __init__(self, methods: dict[str, Callable[..., Any]]) -> None:
        self._methods: dict[str, Callable[..., Any]] = methods
        self._obj_registry: dict[str, type[ImplFunc]] = {}

    def register_overwrite(self, obj: type[ImplFunc]) -> None:
        fn_name = obj.__name__

        if not isinstance(obj, type(ImplFunc)):
            raise ValueError(f"Object '{fn_name}' is not an instance of ImplFunc")

        if fn_name in self._obj_registry:
            raise ValueError(f"Function '{fn_name}' already registered")
        self._obj_registry[fn_name] = obj

    def check_signature(self, method_annotations: dict[str, dict[str, Any]]) -> None:
        overwrite_fns = self._obj_registry

        # iterate over the methods and check if all are implemented
        for m_name, m_annotations in method_annotations.items():
            if m_name not in overwrite_fns:
                continue
            else:
                # check if the signature of the abstract method matches the implementation
                # abstract signature
                values = list(m_annotations.values())
                expected_signature = (tuple(values[:-1]), values[-1:][0])

                # implementation signature
                obj = dict(overwrite_fns[m_name].__dict__)
                obj_type = obj["__orig_bases__"][0]
                got_signature = obj_type.__args__

                if expected_signature != got_signature:
                    log.error(f"Expected signature: {expected_signature}")
                    log.error(f"Actual signature: {got_signature}")
                    raise ValueError(
                        f"Overwritten method '{m_name}' has different signature than the implementation"
                    )

    def get_obj(self, name: str) -> type[ImplFunc]:
        result = self._obj_registry.get(name, None)
        if result is not None:
            return result

        plain_method = self._methods.get(name, None)
        if plain_method is None:
            raise ValueError(f"Method '{name}' not found in Api")

        class GenericFnRuntime(ImplFunc[..., Any]):
            def __init__(self) -> None:
                super().__init__()

            def async_run(self, *args: Any, **kwargs: dict[str, Any]) -> bool:
                assert plain_method is not None
                result = plain_method(*args, **kwargs)
                self.returns(result)
                return GLib.SOURCE_REMOVE

        return cast(type[ImplFunc], GenericFnRuntime)
