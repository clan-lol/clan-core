
import importlib
import inspect
import logging
import pkgutil
from collections.abc import Callable
from types import ModuleType
from typing import Any, ClassVar, Generic, ParamSpec, TypeVar

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


B = TypeVar('B')
P = ParamSpec('P')
class ImplFunc(GObject.Object, Generic[P, B]):
    op_key: str | None = None
    __gsignals__: ClassVar = {
        "returns": (GObject.SignalFlags.RUN_FIRST, None, [GObject.Object]),
    }
    def returns(self, result: B) -> None:
        self.emit("returns", GResult(result, self.__class__.__name__, self.op_key))

    def await_result(self, fn: Callable[[GObject.Object, B], None]) -> None:
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


def is_gobject_subclass(obj: object) -> bool:
    return inspect.isclass(obj) and issubclass(obj, ImplFunc) and obj is not ImplFunc

def check_module_for_gobject_classes(module: ModuleType, found_classes: list[type[GObject.Object]] | None = None) -> list[type[GObject.Object]]:
    if found_classes is None:
        found_classes = []

    for name, obj in inspect.getmembers(module):
        if is_gobject_subclass(obj):
            found_classes.append(obj)

    if hasattr(module, '__path__'):  # Check if the module has submodules
        for _, submodule_name, _ in pkgutil.iter_modules(module.__path__, module.__name__ + '.'):
            submodule = importlib.import_module(submodule_name)
            check_module_for_gobject_classes(submodule, found_classes)

    return found_classes

class ImplApi:
    def __init__(self) -> None:
        self._obj_registry: dict[str, type[ImplFunc]] = {}

    def register_all(self, module: ModuleType) -> None:
        objects = check_module_for_gobject_classes(module)
        for obj in objects:
            self.register(obj)

    def register(self, obj: type[ImplFunc]) -> None:
        fn_name = obj.__name__
        if fn_name in self._obj_registry:
            raise ValueError(f"Function '{fn_name}' already registered")
        self._obj_registry[fn_name] = obj

    def validate(self,
        abstr_methods: dict[str, dict[str, Any]]
    ) -> None:
        impl_fns = self._obj_registry

        # iterate over the methods and check if all are implemented
        for abstr_name, abstr_annotations in abstr_methods.items():
            if abstr_name not in impl_fns:
                raise NotImplementedError(
                    f"Abstract method '{abstr_name}' is not implemented"
                )
            else:
                # check if the signature of the abstract method matches the implementation
                # abstract signature
                values = list(abstr_annotations.values())
                expected_signature = (tuple(values[:-1]), values[-1:][0])

                # implementation signature
                obj = dict(impl_fns[abstr_name].__dict__)
                obj_type = obj["__orig_bases__"][0]
                got_signature = obj_type.__args__

                if expected_signature != got_signature:
                    log.error(f"Expected signature: {expected_signature}")
                    log.error(f"Actual signature: {got_signature}")
                    raise ValueError(
                        f"Abstract method '{abstr_name}' has different signature than the implementation"
                    )

    def get_obj(self, name: str) -> type[ImplFunc] | None:
        return self._obj_registry.get(name)




