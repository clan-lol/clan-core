from collections.abc import Callable


class _MethodRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, fn: Callable) -> Callable:
        self._registry[fn.__name__] = fn
        return fn


API = _MethodRegistry()
