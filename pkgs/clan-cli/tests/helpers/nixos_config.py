from collections import defaultdict
from collections.abc import Callable
from typing import Any


def def_value() -> defaultdict:
    return defaultdict(def_value)


# allows defining nested dictionary in a single line
nested_dict: Callable[[], dict[str, Any]] = lambda: defaultdict(def_value)
