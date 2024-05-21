import dataclasses
import pathlib
from types import NoneType, UnionType
from typing import Any, Union


def type_to_dict(t: Any, scope: str = "") -> dict:
    if t is None:
        return {"type": "null"}

    if dataclasses.is_dataclass(t):
        fields = dataclasses.fields(t)
        properties = {
            f.name: type_to_dict(f.type, f"{scope} {t.__name__}.{f.name}")
            for f in fields
        }
        required = [pn for pn, pv in properties.items() if "null" not in pv["type"]]
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            # Dataclasses can only have the specified properties
            "additionalProperties": False,
        }
    elif type(t) is UnionType:
        return {
            "type": [type_to_dict(arg, scope)["type"] for arg in t.__args__],
        }

    elif hasattr(t, "__origin__"):  # Check if it's a generic type
        origin = getattr(t, "__origin__", None)

        if origin is None:
            # Non-generic user-defined or built-in type
            # TODO: handle custom types
            raise BaseException("Unhandled Type: ", origin)

        elif origin is Union:
            return {"type": [type_to_dict(arg, scope)["type"] for arg in t.__args__]}

        elif issubclass(origin, list):
            return {"type": "array", "items": type_to_dict(t.__args__[0], scope)}

        elif issubclass(origin, dict):
            return {
                "type": "object",
            }

        raise BaseException(f"Error api type not yet supported {t!s}")

    elif isinstance(t, type):
        if t is str:
            return {"type": "string"}
        if t is int:
            return {"type": "integer"}
        if t is float:
            return {"type": "number"}
        if t is bool:
            return {"type": "boolean"}
        if t is object:
            return {"type": "object"}
        if t is Any:
            raise BaseException(
                f"Usage of the Any type is not supported for API functions. In: {scope}"
            )

        if t is pathlib.Path:
            return {
                # TODO: maybe give it a pattern for URI
                "type": "string",
            }

        # Optional[T] gets internally transformed Union[T,NoneType]
        if t is NoneType:
            return {"type": "null"}

        raise BaseException(f"Error primitive type not supported {t!s}")
    else:
        raise BaseException(f"Error type not supported {t!s}")
