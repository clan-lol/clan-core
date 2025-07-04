import json
import os
from copy import deepcopy
from pathlib import Path

# !!! IMPORTANT !!!
# AVOID VERBS NOT IN THIS LIST
# We might restrict this even further to build a consistent and easy to use API
COMMON_VERBS = {
    "get",
    "list",
    "show",
    "set",
    "create",
    "update",
    "delete",
    "generate",
    "maybe",
    "open",
    "flash",
    "install",
    "deploy",
    "check",
    "cancel",
}


def is_verb(word: str) -> bool:
    return word in COMMON_VERBS


def singular(word: str) -> str:
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith("ses"):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


def normalize_tag(parts: list[str]) -> list[str]:
    # parts contains [ VERB NOUN NOUN ... ]
    # Where each NOUN is a SUB-RESOURCE
    verb = parts[0]

    nouns = parts[1:]
    if not nouns:
        nouns = ["misc"]
        # msg = "Operation names MUST have at least one NOUN"
        # raise Error(msg)
    nouns = [singular(p).capitalize() for p in nouns]
    return [verb, *nouns]


def operation_to_tag(op_name: str) -> str:
    def check_operation_name(verb: str, resource_nouns: list[str]):
        if not is_verb(verb):
            print(
                f"""⚠️ WARNING: Verb '{op_name}' of API operation {op_name} is not allowed.
Use one of: {", ".join(COMMON_VERBS)}
"""
            )

    parts = op_name.lower().split("_")
    normalized = normalize_tag(parts)

    check_operation_name(verb=normalized[0], resource_nouns=normalized[1:])

    return " / ".join(normalized[1:])


def fix_nullables(schema: dict) -> dict:
    if isinstance(schema, dict):
        # If 'oneOf' present
        if "oneOf" in schema and isinstance(schema["oneOf"], list):
            # Filter out 'type:null' schemas
            non_nulls = [s for s in schema["oneOf"] if s.get("type") != "null"]
            if len(non_nulls) == 1:
                # Only one non-null schema remains - convert to that + nullable:true
                new_schema = deepcopy(non_nulls[0])
                new_schema["nullable"] = True
                # Merge any other keys from original schema except oneOf
                for k, v in schema.items():
                    if k != "oneOf":
                        new_schema[k] = v
                return fix_nullables(new_schema)
            # More than one non-null, keep oneOf without nulls
            schema["oneOf"] = non_nulls
            return {k: fix_nullables(v) for k, v in schema.items()}
        # Recursively fix nested schemas
        return {k: fix_nullables(v) for k, v in schema.items()}
    if isinstance(schema, list):
        return [fix_nullables(i) for i in schema]
    return schema


def fix_error_refs(schema: dict) -> None:
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key == "$ref" and value == "#/$defs/error":
                schema[key] = "#/components/schemas/error"
            else:
                fix_error_refs(value)
    elif isinstance(schema, list):
        for item in schema:
            fix_error_refs(item)


# === Helper to make reusable schema names ===
def make_schema_name(func_name: str, part: str) -> str:
    return f"{func_name}_{part}"


def main() -> None:
    INPUT_PATH = Path(os.environ["INPUT_PATH"])

    # === Load input JSON Schema ===
    with INPUT_PATH.open() as f:
        schema = json.load(f)

    defs = schema.get("$defs", {})
    functions = schema["properties"]

    # === Start OpenAPI 3.0 spec in JSON ===
    openapi = {
        "openapi": "3.0.3",
        "info": {
            "title": "Function-Based API",
            "version": "1.0.0",
            "description": "Auto-generated OpenAPI 3.0 spec from custom JSON Schema",
        },
        "paths": {},
        "components": {"schemas": {}},
    }

    # === Convert each function ===
    for func_name, func_schema in functions.items():
        args_schema = fix_nullables(deepcopy(func_schema["properties"]["arguments"]))
        return_schema = fix_nullables(deepcopy(func_schema["properties"]["return"]))
        fix_error_refs(return_schema)
        # Register schemas under components
        args_name = make_schema_name(func_name, "args")
        return_name = make_schema_name(func_name, "return")
        openapi["components"]["schemas"][args_name] = args_schema
        openapi["components"]["schemas"][return_name] = return_schema
        tag = operation_to_tag(func_name)
        # Create a POST endpoint for the function
        openapi["paths"][f"/{func_name}"] = {
            "post": {
                "summary": func_name,
                "operationId": func_name,
                "tags": [tag],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{args_name}"}
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{return_name}"
                                }
                            }
                        },
                    }
                },
            }
        }

    # === Add global definitions from $defs ===
    for def_name, def_schema in defs.items():
        fixed_schema = fix_nullables(deepcopy(def_schema))
        fix_error_refs(fixed_schema)
        openapi["components"]["schemas"][def_name] = fixed_schema

    # === Write to output JSON ===
    with Path("openapi.json").open("w") as f:
        json.dump(openapi, f, indent=2)

    print("✅ OpenAPI 3.0 JSON written to openapi.json")


if __name__ == "__main__":
    main()
