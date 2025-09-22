from typing import NotRequired, Required, get_args, get_origin, get_type_hints


def is_typeddict_class(obj: type) -> bool:
    """Safely checks if a class is a TypedDict."""
    return (
        isinstance(obj, type)
        and hasattr(obj, "__annotations__")
        and obj.__class__.__name__ == "_TypedDictMeta"
    )


def retrieve_typed_field_names(obj: type, prefix: str = "") -> set[str]:
    fields = set()
    hints = get_type_hints(obj, include_extras=True)

    for field, field_type in hints.items():
        full_key = f"{prefix}.{field}" if prefix else field

        origin = get_origin(field_type)
        args = get_args(field_type)

        # Unwrap Required/NotRequired
        if origin in {NotRequired, Required}:
            unwrapped_type = args[0]
            origin = get_origin(unwrapped_type)
            args = get_args(unwrapped_type)
        else:
            unwrapped_type = field_type

        if is_typeddict_class(unwrapped_type):
            fields |= retrieve_typed_field_names(unwrapped_type, prefix=full_key)
        else:
            fields.add(full_key)

    return fields
