from collections.abc import Callable
from types import ModuleType
from typing import Any


class FakeDeal:
    def __getattr__(self, name: str) -> "Callable":
        return self.mock_call

    def mock_call(self, *args: Any, **kwargs: Any) -> Callable:
        def wrapper(func: Callable) -> Callable:
            return func

        return wrapper


try:
    import deal as real_deal

    deal: ModuleType | FakeDeal = real_deal
except ImportError:
    deal = FakeDeal()
