from collections.abc import Callable
from types import ModuleType
from typing import Any, Protocol


class AnyCall(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        ...


class FakeDeal:
    def __getattr__(self, name: str) -> AnyCall:
        return self.mock_call

    def mock_call(self, *args: Any, **kwargs: Any) -> Callable[[AnyCall], AnyCall]:
        def wrapper(func: AnyCall) -> AnyCall:
            return func

        return wrapper


try:
    import deal as real_deal

    deal: ModuleType | FakeDeal = real_deal
except ImportError:
    deal = FakeDeal()
