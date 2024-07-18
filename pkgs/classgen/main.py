# ruff: noqa: RUF001
import argparse
import json
from typing import Any


# Function to map JSON schemas and types to Python types
def map_json_type(
    json_type: Any, nested_types: set[str] = {"Any"}, parent: Any = None
) -> set[str]:
    if isinstance(json_type, list):
        res = set()
        for t in json_type:
            res |= map_json_type(t)
        return res
    if isinstance(json_type, dict):
        return map_json_type(json_type.get("type"))
    elif json_type == "string":
        return {"str"}
    elif json_type == "integer":
        return {"int"}
    elif json_type == "boolean":
        return {"bool"}
    elif json_type == "array":
        assert nested_types, f"Array type not found for {parent}"
        return {f"""list[{" | ".join(nested_types)}]"""}
    elif json_type == "object":
        assert nested_types, f"dict type not found for {parent}"
        return {f"""dict[str, {" | ".join(nested_types)}]"""}
    elif json_type == "null":
        return {"None"}
    else:
        raise ValueError(f"Python type not found for {json_type}")


known_classes = set()
root_class = "Inventory"


# Recursive function to generate dataclasses from JSON schema
def generate_dataclass(schema: dict[str, Any], class_name: str = root_class) -> str:
    properties = schema.get("properties", {})

    required_fields = []
    fields_with_default = []
    nested_classes = []

    for prop, prop_info in properties.items():
        field_name = prop.replace("-", "_")

        prop_type = prop_info.get("type", None)
        union_variants = prop_info.get("oneOf", [])
        # Collect all types
        field_types = set()

        title = prop_info.get("title", prop.removesuffix("s"))
        title_sanitized = "".join([p.capitalize() for p in title.split("-")])
        nested_class_name = f"""{class_name if class_name != root_class and not prop_info.get("title") else ""}{title_sanitized}"""

        if (prop_type is None) and (not union_variants):
            raise ValueError(f"Type not found for property {prop} {prop_info}")

        if union_variants:
            field_types = map_json_type(union_variants)

        elif prop_type == "array":
            item_schema = prop_info.get("items")

            if isinstance(item_schema, dict):
                field_types = map_json_type(
                    prop_type, map_json_type(item_schema), field_name
                )

        elif prop_type == "object":
            inner_type = prop_info.get("additionalProperties")
            if inner_type and inner_type.get("type") == "object":
                # Inner type is a class
                field_types = map_json_type(prop_type, {nested_class_name}, field_name)

                #
                if nested_class_name not in known_classes:
                    nested_classes.append(
                        generate_dataclass(inner_type, nested_class_name)
                    )
                    known_classes.add(nested_class_name)

            elif inner_type and inner_type.get("type") != "object":
                # Trivial type
                field_types = map_json_type(inner_type)

            elif not inner_type:
                # The type is a class
                field_types = {nested_class_name}
                if nested_class_name not in known_classes:
                    nested_classes.append(
                        generate_dataclass(prop_info, nested_class_name)
                    )
                    known_classes.add(nested_class_name)
        else:
            field_types = map_json_type(
                prop_type,
                nested_types=set(),
                parent=field_name,
            )

        assert field_types, f"Python type not found for {prop} {prop_info}"

        serialised_types = " | ".join(field_types)
        field_meta = None
        if field_name != prop:
            field_meta = f"""{{"original_name": "{prop}"}}"""

        field_def = f"{field_name}: {serialised_types}"
        if field_meta:
            field_def = f"{field_def} = field(metadata={field_meta})"

        if "default" in prop_info or field_name not in prop_info.get("required", []):
            if "default" in prop_info:
                default_value = prop_info.get("default")
                if default_value is None:
                    field_types |= {"None"}
                    serialised_types = " | ".join(field_types)

                    field_def = f"""{field_name}: {serialised_types} = field(default=None {f", metadata={field_meta}" if field_meta else ""})"""
                elif isinstance(default_value, list):
                    field_def = f"""{field_def} = field(default_factory=list {f", metadata={field_meta}" if field_meta else ""})"""
                elif isinstance(default_value, dict):
                    serialised_types = " | ".join(field_types)
                    if serialised_types == nested_class_name:
                        field_def = f"""{field_name}: {serialised_types} = field(default_factory={nested_class_name} {f", metadata={field_meta}" if field_meta else ""})"""
                    elif f"dict[str, {nested_class_name}]" in serialised_types:
                        field_def = f"""{field_name}: {serialised_types} = field(default_factory=dict {f", metadata={field_meta}" if field_meta else ""})"""
                    else:
                        field_def = f"""{field_name}: {serialised_types} | dict[str,Any] = field(default_factory=dict {f", metadata={field_meta}" if field_meta else ""})"""
                elif default_value == "‹name›":
                    # Special case for nix submodules
                    pass
                elif isinstance(default_value, str):
                    field_def = f"""{field_name}: {serialised_types} = field(default = '{default_value}' {f", metadata={field_meta}" if field_meta else ""})"""
                else:
                    # Other default values unhandled yet.
                    raise ValueError(
                        f"Unhandled default value for field '{field_name}' - default value: {default_value}"
                    )

                fields_with_default.append(field_def)

            if "default" not in prop_info:
                # Field is not required and but also specifies no default value
                # Trying to infer default value from type
                if "dict" in str(serialised_types):
                    field_def = f"""{field_name}: {serialised_types} = field(default_factory=dict {f", metadata={field_meta}" if field_meta else ""})"""
                    fields_with_default.append(field_def)
                elif "list" in str(serialised_types):
                    field_def = f"""{field_name}: {serialised_types} = field(default_factory=list {f", metadata={field_meta}" if field_meta else ""})"""
                    fields_with_default.append(field_def)
                elif "None" in str(serialised_types):
                    field_def = f"""{field_name}: {serialised_types} = field(default=None {f", metadata={field_meta}" if field_meta else ""})"""
                    fields_with_default.append(field_def)
                else:
                    # Field is not required and but also specifies no default value
                    required_fields.append(field_def)
        else:
            required_fields.append(field_def)

    fields_str = "\n    ".join(required_fields + fields_with_default)
    nested_classes_str = "\n\n".join(nested_classes)

    class_def = f"@dataclass\nclass {class_name}:\n    {fields_str}\n"
    return f"{nested_classes_str}\n\n{class_def}" if nested_classes_str else class_def


def run_gen(args: argparse.Namespace) -> None:
    print(f"Converting {args.input} to {args.output}")
    dataclass_code = ""
    with open(args.input) as f:
        schema = json.load(f)
        dataclass_code = generate_dataclass(schema)

    with open(args.output, "w") as f:
        f.write(
            """
# DON NOT EDIT THIS FILE MANUALLY. IT IS GENERATED.
# UPDATE
# ruff: noqa: N815
# ruff: noqa: N806
from dataclasses import dataclass, field
from typing import Any\n\n
"""
        )
        f.write(dataclass_code)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input JSON schema file")
    parser.add_argument("output", help="Output Python file")
    parser.set_defaults(func=run_gen)

    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
