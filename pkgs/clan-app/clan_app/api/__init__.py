import inspect
import logging
import threading
from collections.abc import Callable
from typing import (
    Any,
    ClassVar,
    Generic,
    ParamSpec,
    TypeVar,
    cast,
)

from gi.repository import GLib, GObject

log = logging.getLogger(__name__)


class GResult(GObject.Object):
    result: Any
    op_key: str
    method_name: str

    def __init__(self, result: Any, method_name: str) -> None:
        super().__init__()
        self.result = result
        self.method_name = method_name


B = TypeVar("B")
P = ParamSpec("P")


class ImplFunc(GObject.Object, Generic[P, B]):
    op_key: str | None = None
    __gsignals__: ClassVar = {
        "returns": (GObject.SignalFlags.RUN_FIRST, None, [GResult]),
    }

    def returns(self, result: B, *, method_name: str | None = None) -> None:
        if method_name is None:
            method_name = self.__class__.__name__

        self.emit("returns", GResult(result, method_name))

    def await_result(self, fn: Callable[["ImplFunc[..., Any]", B], None]) -> None:
        self.connect("returns", fn)

    def async_run(self, *args: P.args, **kwargs: P.kwargs) -> bool:
        raise NotImplementedError("Method 'async_run' must be implemented")

    def _async_run(self, data: Any) -> bool:
        result = GLib.SOURCE_REMOVE
        try:
            result = self.async_run(**data)
        except Exception as e:
            log.exception(e)
            # TODO: send error to js
        finally:
            return result


class MethodExecutor(threading.Thread):
    def __init__(
        self, function: Callable[..., Any], *args: Any, **kwargs: dict[str, Any]
    ) -> None:
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.result: Any = None
        self.finished = False

    def run(self) -> None:
        try:
            self.result = self.function(*self.args, **self.kwargs)
        except Exception as e:
            log.exception(e)
        finally:
            self.finished = True


class GObjApi:
    def __init__(self, methods: dict[str, Callable[..., Any]]) -> None:
        self._methods: dict[str, Callable[..., Any]] = methods
        self._obj_registry: dict[str, type[ImplFunc]] = {}

    def overwrite_fn(self, obj: type[ImplFunc]) -> None:
        fn_name = obj.__name__

        if fn_name in self._obj_registry:
            raise ValueError(f"Function '{fn_name}' already registered")
        self._obj_registry[fn_name] = obj

    def check_signature(self, fn_signatures: dict[str, inspect.Signature]) -> None:
        overwrite_fns = self._obj_registry

        # iterate over the methods and check if all are implemented
        for m_name, m_signature in fn_signatures.items():
            if m_name not in overwrite_fns:
                continue
            else:
                # check if the signature of the overriden method matches
                # the implementation signature
                exp_args = []
                exp_return = m_signature.return_annotation
                for param in dict(m_signature.parameters).values():
                    exp_args.append(param.annotation)
                exp_signature = (tuple(exp_args), exp_return)

                # implementation signature
                obj = dict(overwrite_fns[m_name].__dict__)
                obj_type = obj["__orig_bases__"][0]
                got_signature = obj_type.__args__

                if exp_signature != got_signature:
                    log.error(f"Expected signature: {exp_signature}")
                    log.error(f"Actual signature: {got_signature}")
                    raise ValueError(
                        f"Overwritten method '{m_name}' has different signature than the implementation"
                    )

    def get_obj(self, fn_name: str) -> type[ImplFunc]:
        result = self._obj_registry.get(fn_name, None)
        if result is not None:
            return result

        plain_fn = self._methods.get(fn_name, None)
        if plain_fn is None:
            raise ValueError(f"Method '{fn_name}' not found in Api")

        class GenericFnRuntime(ImplFunc[..., Any]):
            def __init__(self) -> None:
                super().__init__()
                self.thread: MethodExecutor | None = None

            def async_run(self, *args: Any, **kwargs: dict[str, Any]) -> bool:
                assert plain_fn is not None

                if self.thread is None:
                    self.thread = MethodExecutor(plain_fn, *args, **kwargs)
                    self.thread.start()
                    return GLib.SOURCE_CONTINUE
                elif self.thread.finished:
                    result = self.thread.result
                    self.returns(method_name=fn_name, result=result)
                    return GLib.SOURCE_REMOVE
                else:
                    return GLib.SOURCE_CONTINUE

        return cast(type[ImplFunc], GenericFnRuntime)
