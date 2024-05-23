from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")


class _MethodRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, Callable] = {}

    def register(self, fn: Callable[..., T]) -> Callable[..., T]:
        self._registry[fn.__name__] = fn
        return fn

    def to_json_schema(self) -> str:
        # Import only when needed
        import json
        from typing import get_type_hints

        from clan_cli.api.util import type_to_dict

        api_schema: dict[str, Any] = {
            "$comment": "An object containing API methods. ",
            "type": "object",
            "additionalProperties": False,
            "required": ["list_machines"],
            "properties": {},
        }
        for name, func in self._registry.items():
            hints = get_type_hints(func)
            serialized_hints = {
                "argument" if key != "return" else "return": type_to_dict(
                    value, scope=name + " argument" if key != "return" else "return"
                )
                for key, value in hints.items()
            }
            api_schema["properties"][name] = {
                "type": "object",
                "required": [k for k in serialized_hints.keys()],
                "additionalProperties": False,
                "properties": {**serialized_hints},
            }

        return json.dumps(api_schema, indent=2)


API = _MethodRegistry()
