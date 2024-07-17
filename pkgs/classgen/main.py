import argparse
import json
from typing import Any


# Function to map JSON schema types to Python types
def map_json_type(json_type: Any, nested_type: str = "Any") -> str:
    if isinstance(json_type, list):
        return " | ".join(map(map_json_type, json_type))
    if isinstance(json_type, dict):
        return map_json_type(json_type.get("type"))
    elif json_type == "string":
        return "str"
    elif json_type == "integer":
        return "int"
    elif json_type == "boolean":
        return "bool"
    elif json_type == "array":
        return f"list[{nested_type}]"  # Further specification can be handled if needed
    elif json_type == "object":
        return f"dict[str, {nested_type}]"
    elif json_type == "null":
        return "None"
    else:
        return "Any"


known_classes = set()
root_class = "Inventory"


# Recursive function to generate dataclasses from JSON schema
def generate_dataclass(schema: dict[str, Any], class_name: str = root_class) -> str:
    properties = schema.get("properties", {})
    required = schema.get("required", [])

    fields = []
    nested_classes = []

    for prop, prop_info in properties.items():
        field_name = prop.replace("-", "_")

        prop_type = prop_info.get("type", None)
        union_variants = prop_info.get("oneOf", [])

        title = prop_info.get("title", prop.removesuffix("s"))
        title_sanitized = "".join([p.capitalize() for p in title.split("-")])
        nested_class_name = f"""{class_name if class_name != root_class and not prop_info.get("title") else ""}{title_sanitized}"""

        # if nested_class_name == "ServiceBorgbackupRoleServerConfig":
        #     breakpoint()

        if (prop_type is None) and (not union_variants):
            raise ValueError(f"Type not found for property {prop} {prop_info}")

        # Unions fields (oneOf)
        # str | int | None
        python_type = None

        if union_variants:
            python_type = map_json_type(union_variants)
        elif prop_type == "array":
            item_schema = prop_info.get("items")
            if isinstance(item_schema, dict):
                python_type = map_json_type(
                    prop_type,
                    map_json_type(item_schema),
                )
        else:
            python_type = map_json_type(
                prop_type,
                map_json_type([i for i in prop_info.get("items", [])]),
            )

        assert python_type, f"Python type not found for {prop} {prop_info}"

        if prop in required:
            field_def = f"{prop}: {python_type}"
        else:
            field_def = f"{prop}: {python_type} | None = None"

        if prop_type == "object":
            map_type = prop_info.get("additionalProperties")
            if map_type:
                # breakpoint()
                if map_type.get("type") == "object":
                    # Non trivial type
                    if nested_class_name not in known_classes:
                        nested_classes.append(
                            generate_dataclass(map_type, nested_class_name)
                        )
                        known_classes.add(nested_class_name)
                    field_def = f"{field_name}: dict[str, {nested_class_name}]"
                else:
                    # Trivial type
                    field_def = f"{field_name}: dict[str, {map_json_type(map_type)}]"
            else:
                if nested_class_name not in known_classes:
                    nested_classes.append(
                        generate_dataclass(prop_info, nested_class_name)
                    )
                    known_classes.add(nested_class_name)

                field_def = f"{field_name}: {nested_class_name}"

        elif prop_type == "array":
            items = prop_info.get("items", {})
            if items.get("type") == "object":
                nested_class_name = prop.capitalize()
                nested_classes.append(generate_dataclass(items, nested_class_name))
                field_def = f"{field_name}: List[{nested_class_name}]"

        fields.append(field_def)

    fields_str = "\n    ".join(fields)
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
from dataclasses import dataclass
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
