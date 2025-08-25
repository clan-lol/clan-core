import argparse
import json
import logging
import traceback
from collections.abc import Callable, Iterable
from functools import partial
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class Error(Exception):
    pass


def sort_types(items: Iterable[str]) -> list[str]:
    def sort_key(item: str) -> tuple[int, str]:
        # Priority order: lower number = higher priority
        if item.startswith(("dict", "list")):
            return (0, item)  # Highest priority, dicts and lists should be first
        if item == "None":
            return (2, item)  # Lowest priority, None should be last
        return (1, item)  # Middle priority, sorted alphabetically

    return sorted(items, key=sort_key)


# Function to map JSON schemas and types to Python types
def map_json_type(
    json_type: Any,
    nested_types: list[str] | None = None,
    parent: Any = None,
) -> list[str]:
    if nested_types is None:
        nested_types = ["Any"]
    if isinstance(json_type, list):
        res: list[str] = []
        for t in json_type:
            res.extend(map_json_type(t))
        return sort_types(set(res))

    if isinstance(json_type, dict):
        items = json_type.get("items")
        if items:
            nested_types = map_json_type(items)

        if not json_type.get("type") and json_type.get("tsType") == "unknown":
            return ["Unknown"]

        union = json_type.get("oneOf")
        if union:
            res: list[str] = []
            for t in union:
                res.extend(map_json_type(t, nested_types, parent))
            return sort_types(set(res))

        return sort_types(map_json_type(json_type.get("type"), nested_types))
    if json_type == "string":
        return ["str"]
    if json_type == "integer":
        return ["int"]
    if json_type == "number":
        return ["float"]
    if json_type == "boolean":
        return ["bool"]
    # In Python, "number" is analogous to the float type.
    # https://json-schema.org/understanding-json-schema/reference/numeric#number
    if json_type == "number":
        return ["float"]
    if json_type == "array":
        if not nested_types:
            msg = f"Array type not found for {parent}"
            raise Error(msg)
        return [f"""list[{" | ".join(sort_types(nested_types))}]"""]
    if json_type == "object":
        if not nested_types:
            msg = f"dict type not found for {parent}"
            raise Error(msg)
        return [f"""dict[str, {" | ".join(sort_types(nested_types))}]"""]
    if json_type == "null":
        return ["None"]

    msg = f"Python type not found for {json_type}"
    raise Error(msg)


known_classes = set()
# TODO: make this configurable
root_class = "Clan"


def field_def_from_default_type(
    field_name: str,
    field_types: list[str],
    class_name: str,
    finalize_field: Callable[..., tuple[str, str]],
) -> tuple[str, str] | None:
    if "dict" in str(field_types):
        return finalize_field(
            field_types=field_types,
            default_factory="dict",
        )

    if "list" in str(field_types):
        return finalize_field(
            field_types=field_types,
            default_factory="list",
        )
    if "None" in str(field_types):
        return finalize_field(
            field_types=field_types,
            default="None",
        )

    if class_name.endswith("Config"):
        # SingleDiskConfig
        # PackagesConfig
        # ...
        # Config classes MUST always be optional
        msg = f"""
            #################################################
            Clan module '{class_name}' specifies a top-level option '{field_name}' without a default value.

            To fix this:
            - Add a default value to the option

            lib.mkOption {{
                type = lib.types.nullOr lib.types.str;
                default = null; # <- Add a default value here
            }};

            # Other options

            - make the field nullable

            lib.mkOption {{
                #      ╔══════════════╗ <- Nullable type
                type = lib.types.nullOr lib.types.str;
            }};

            - Use lib.types.attrsOf if suitable
            - Use lib.types.listOf if suitable


            Or report this problem to the clan team. So the class generator can be improved.
            #################################################
            """
        raise Error(msg)

    return None


def field_def_from_default_value(
    default_value: Any,
    field_name: str,
    field_types: list[str],
    nested_class_name: str,
    finalize_field: Callable[..., tuple[str, str]],
) -> tuple[str, str] | None:
    # default_value = prop_info.get("default")
    if "Unknown" in field_types:
        # Unknown type, doesnt matter what the default value is
        # type Unknown | a -> Unknown
        return finalize_field(
            field_types=field_types,
        )
    if default_value is None:
        return finalize_field(
            field_types=[*field_types, "None"],
            default="None",
        )
    if isinstance(default_value, list):
        return finalize_field(
            field_types=field_types,
            default_factory="list",
        )
    if isinstance(default_value, dict):
        serialised_types = " | ".join(field_types)
        if serialised_types == nested_class_name:
            return finalize_field(
                field_types=field_types,
                default_factory=nested_class_name,
            )

        if "dict[str," in serialised_types:
            return finalize_field(
                field_types=field_types,
                default_factory="dict",
            )
        return finalize_field(
            field_types=field_types,
            default_factory="dict",
            type_appendix=" | dict[str,Any]",
        )

    # Primitive types
    if isinstance(default_value, str):
        return finalize_field(
            field_types=field_types,
            default=f"'{default_value}'",
        )
    if isinstance(default_value, bool | int | float):
        # Bool must be checked before int
        return finalize_field(
            field_types=field_types,
            default=f"{default_value}",
        )

    # Other default values unhandled yet.
    msg = f"Unhandled default value for field '{field_name}' - default value: {default_value}. ( In {nested_class_name} )"
    raise Error(msg)


def get_field_def(
    field_name: str,
    field_types: list[str],
    default: str | None = None,
    default_factory: str | None = None,
    type_appendix: str = "",
) -> tuple[str, str]:
    if "None" in field_types or default or default_factory:
        if "None" in field_types:
            field_types.remove("None")
        serialised_types = " | ".join(sort_types(field_types)) + type_appendix
        serialised_types = f"{serialised_types}"
    else:
        serialised_types = " | ".join(sort_types(field_types)) + type_appendix

    return (field_name, serialised_types)


# Recursive function to generate dataclasses from JSON schema
def generate_dataclass(
    schema: dict[str, Any],
    attr_path: list[str],
    class_name: str = root_class,
) -> str:
    properties = schema.get("properties", {})

    required_fields: list[tuple[str, str]] = []
    fields_with_default: list[tuple[str, str]] = []
    nested_classes: list[str] = []

    for prop, prop_info in properties.items():
        # If we are at the top level, and the attribute name is not explicitly included we only do shallow
        field_name = prop.replace("-", "_")

        # if len(attr_path) == 0 and prop in shallow_attrs:
        #     field_def = field_name, "dict[str, Any]"
        #     fields_with_default.append(field_def)
        #     continue

        prop_type = prop_info.get("type", None)
        union_variants = prop_info.get("oneOf", [])
        enum_variants = prop_info.get("enum", [])

        # Collect all types
        field_types: list[str] = []

        title = prop_info.get("title", prop.removesuffix("s"))
        title_sanitized = "".join([p.capitalize() for p in title.split("-")])
        nested_class_name = f"""{class_name if class_name != root_class and not prop_info.get("title") else ""}{title_sanitized}"""

        if not prop_type and not union_variants and not enum_variants:
            msg = f"Type not found for property {prop} {prop_info}.\nConverting to unknown type.\n"
            logger.warning(msg)
            prop_type = "Unknown"

        if union_variants:
            field_types = map_json_type(union_variants)

        elif prop_type == "array":
            item_schema = prop_info.get("items")

            if isinstance(item_schema, dict):
                field_types = map_json_type(
                    prop_type,
                    map_json_type(item_schema),
                    field_name,
                )
        elif enum := prop_info.get("enum"):
            literals = ", ".join([f'"{string}"' for string in enum])
            field_types = [f"""Literal[{literals}]"""]

        elif prop_type == "object":
            inner_type = prop_info.get("additionalProperties")
            if inner_type and inner_type.get("type") == "object":
                # Inner type is a class
                field_types = map_json_type(prop_type, [nested_class_name], field_name)

                if nested_class_name not in known_classes:
                    nested_classes.append(
                        generate_dataclass(
                            inner_type,
                            [*attr_path, prop],
                            nested_class_name,
                        ),
                    )
                    known_classes.add(nested_class_name)

            elif inner_type and inner_type.get("type") != "object":
                # Trivial type:
                # dict[str, inner_type]
                field_types = [
                    f"""dict[str, {" | ".join(map_json_type(inner_type))}]""",
                ]

            elif not inner_type:
                # The type is a class
                field_types = [nested_class_name]
                if nested_class_name not in known_classes:
                    nested_classes.append(
                        generate_dataclass(
                            prop_info,
                            [*attr_path, prop],
                            nested_class_name,
                        ),
                    )
                    known_classes.add(nested_class_name)
        elif prop_type == "Unknown":
            field_types = ["Unknown"]
        else:
            field_types = map_json_type(
                prop_type,
                nested_types=[],
                parent=field_name,
            )

        if not field_types:
            msg = f"Python type not found for {prop} {prop_info}"
            raise Error(msg)

        finalize_field = partial(get_field_def, field_name)

        # Sort and remove potential duplicates
        field_types_sorted = sort_types(set(field_types))

        if "default" in prop_info or field_name not in prop_info.get("required", []):
            if prop_info.get("type") == "object":
                prop_info.update({"default": {}})

            if "default" in prop_info:
                default_value = prop_info.get("default")
                field_def = field_def_from_default_value(
                    default_value=default_value,
                    field_name=field_name,
                    field_types=field_types_sorted,
                    nested_class_name=nested_class_name,
                    finalize_field=finalize_field,
                )
                if field_def:
                    fields_with_default.append(field_def)

                if not field_def:
                    # Finalize without the default value
                    field_def = finalize_field(
                        field_types=field_types_sorted,
                    )
                    required_fields.append(field_def)

            if "default" not in prop_info:
                # Field is not required and but also specifies no default value
                # Trying to infer default value from type
                field_def = field_def_from_default_type(
                    field_name=field_name,
                    field_types=field_types_sorted,
                    class_name=class_name,
                    finalize_field=finalize_field,
                )

                if field_def:
                    fields_with_default.append(field_def)
                if not field_def:
                    field_def = finalize_field(
                        field_types=field_types_sorted,
                    )
                    required_fields.append(field_def)

        else:
            field_def = finalize_field(
                field_types=field_types_sorted,
            )
            required_fields.append(field_def)

    # Join field name with type to form a complete field declaration
    # e.g. "name: str"
    all_field_declarations = [f"{n}: {t}" for n, t in (required_fields)] + [
        f"{n}: NotRequired[{class_name}{n.capitalize()}Type]"
        for n, t in (fields_with_default)
    ]
    hoisted_types: str = "\n".join(
        [
            f"{class_name}{n.capitalize()}Type = {x}"
            for n, x in (required_fields + fields_with_default)
        ],
    )
    fields_str = "\n    ".join(all_field_declarations)
    nested_classes_str = "\n\n".join(nested_classes)

    class_def = f"\n\n{hoisted_types}\n"
    class_def += f"\nclass {class_name}(TypedDict):\n"
    if not required_fields + fields_with_default:
        class_def += "    pass"
    else:
        class_def += f"    {fields_str}"

    return f"{nested_classes_str}\n\n{class_def}" if nested_classes_str else class_def


def run_gen(args: argparse.Namespace) -> None:
    print(f"Converting {args.input} to {args.output}")

    dataclass_code = ""
    with args.input.open() as f:
        schema = json.load(f)
        dataclass_code = generate_dataclass(schema, [])

    with args.output.open("w") as f:
        f.write(
            """# DO NOT EDIT THIS FILE MANUALLY. IT IS GENERATED.
# This file was generated by running `pkgs/clan-cli/clan_lib.inventory/update.sh`
#
# ruff: noqa: N815
# ruff: noqa: N806
# ruff: noqa: F401
# fmt: off
from typing import Any, Literal, NotRequired, TypedDict\n

# Mimic "unknown".
# 'Any' is unsafe because it allows any operations
# This forces the user to use type-narrowing or casting in the code
class Unknown:
    pass
""",
        )
        f.write(dataclass_code)
        f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input JSON schema file", type=Path)
    parser.add_argument("output", help="Output Python file", type=Path)
    parser.add_argument(
        "--stop-at",
        type=str,
        help="Property name to stop generating classes for. Other classes below that property will be generated",
        default=None,
    )
    parser.set_defaults(func=run_gen)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print("An error occurred:")
        traceback.print_exc()
