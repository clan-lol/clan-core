from types import ModuleType
from typing import Callable


class FakeDeal:
    def __getattr__(self, _name: str) -> "FakeDeal":
        return FakeDeal()

    def __call__(self, func: Callable) -> Callable:
        return func


try:
    import deal as real_deal

    deal: ModuleType | FakeDeal = real_deal
except ImportError:
    deal = FakeDeal()
