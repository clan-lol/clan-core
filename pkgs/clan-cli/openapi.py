import json
import os
from copy import deepcopy
from pathlib import Path

# !!! IMPORTANT !!!
# AVOID VERBS NOT IN THIS LIST
# IF YOU WANT TO ADD TO THIS LIST CREATE AN ISSUE/DISCUSS FIRST
#
# Verbs are restricted to make API usage intuitive and consistent.
#
# Discouraged verbs:
# do        Too vague
# process   Sounds generic; lacks clarity.
# generate  Ambiguous: does it mutate state or not? Prefer 'run'
# handle    Abstract and fuzzy
# show      overlaps with get or list
# describe  overlap with get or list
# can, is   often used for helpers, use check instead for structure responses
COMMON_VERBS = {
    "get",  # fetch single item
    "list",  # fetch collection
    "create",  # instantiate resource
    "set",  # update or configure
    "delete",  # remove resource
    "check",  # validate, probe, or assert
    "run",  # start imperative task or action; machine-deploy etc.
}


# !!! IMPORTANT !!!
# AVOID ADDING RESOUCRCES IN THIS LIST
# Think twice before adding a new resource.
# If you need a new resource, consider if it can be a sub-resource of an existing
# resource instead.
# If you need a new top-level resource, create an issue to discuss it first.
TOP_LEVEL_RESOURCES = {
    "clan",  # clan management
    "tag",  # Tags
    "machine",  # machine management
    "task",  # task management
    "secret",  # sops & key operations
    "log",  # log operations
    "generator",  # vars generators operations
    "service",  # clan.service management
    "system",  # system operations
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


def normalize_op_name(op_name: str) -> list[str]:
    parts = op_name.lower().split("_")
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


def check_operation_name(op_name: str, normalized: list[str]) -> list[str]:
    verb = normalized[0]
    nouns = normalized[1:]
    warnings = []
    if not is_verb(verb):
        warnings.append(
            f"""Verb '{verb}' of API operation {op_name} is not allowed.
Use one of: {", ".join(COMMON_VERBS)}
""",
        )
    top_level_noun = nouns[0] if nouns else None
    if top_level_noun is None or top_level_noun.lower() not in TOP_LEVEL_RESOURCES:
        warnings.append(
            f"""Top-level resource '{top_level_noun}' of API operation {op_name} is not allowed.
Use one of: {", ".join(TOP_LEVEL_RESOURCES)}
""",
        )
    return warnings


def operation_to_tag(op_name: str) -> str:
    normalized = normalize_op_name(op_name)
    return " / ".join(normalized[1:])


def fix_nullables(schema: dict) -> dict:
    if isinstance(schema, dict):
        if "type" in schema and schema["type"] == "null":
            # Convert 'type: null' to 'nullable: true'
            # Merge any other keys from original schema except type
            new_schema = {"nullable": True} | {
                k: v for k, v in schema.items() if k != "type"
            }
            return fix_nullables(new_schema)

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


def fix_empty_required(schema: dict) -> dict:
    """Recursively remove "required: []" from schemas
    This is valid in json schema, but leads to errors in some OpenAPI 3.0 renderers.
    """
    if isinstance(schema, dict):
        if "required" in schema and schema["required"] == []:
            # Remove empty required list
            new_schema = {k: v for k, v in schema.items() if k != "required"}
            return fix_empty_required(new_schema)

        # If 'oneOf' present
        if "oneOf" in schema and isinstance(schema["oneOf"], list):
            # Recursively fix each schema in oneOf
            schema["oneOf"] = [fix_empty_required(s) for s in schema["oneOf"]]
            # Remove empty required from each oneOf schema
            schema["oneOf"] = [
                s
                for s in schema["oneOf"]
                if not (isinstance(s, dict) and s.get("required") == [])
            ]
            return schema

        return {k: fix_empty_required(v) for k, v in schema.items()}

    if isinstance(schema, list):
        return schema  # ignore lists

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


def get_tag_key(tags: list[str]) -> tuple:
    """Convert list of tags to a tuple key for sorting."""
    return tuple(tags)


def sort_openapi_paths_by_tag_tree(openapi: dict) -> None:
    # Extract (tags, path, method, operation) tuples
    operations = []

    for path, methods in openapi["paths"].items():
        for method, operation in methods.items():
            tag_path = operation.get("tags", [])
            operations.append((tag_path, path, method, operation))

    # Sort by the tag hierarchy
    operations.sort(key=lambda x: get_tag_key(x[0]))

    # Rebuild sorted openapi["paths"]
    sorted_paths: dict = {}
    for _tag_path, path, method, operation in operations:
        sorted_paths[path] = sorted_paths.get(path, {})
        sorted_paths[path][method] = operation

    openapi["paths"] = dict(sorted_paths)  # Ensure it's a plain dict


def main() -> None:
    input_path = Path(os.environ["INPUT_PATH"])

    # === Load input JSON Schema ===
    with input_path.open() as f:
        schema = json.load(f)

    defs = schema.get("$defs", {})
    functions = schema["properties"]

    # === Start OpenAPI 3.0 spec in JSON ===
    openapi = {
        "openapi": "3.0.3",
        "info": {
            "title": "Function-Based Python API",
            "version": "1.0.0",
            "description": "!!! INTERNAL USE ONLY !!! We don't provide a world usable API yet.\nThis prototype maps python function calls to POST Requests because we are planning towards RESTfull API in the future.",
        },
        "paths": {},
        "components": {"schemas": {}},
    }

    # === Check all functions ===
    warnings: list[str] = []
    errors: list[str] = []
    for func_name, func_schema in functions.items():
        normalized = normalize_op_name(func_name)
        check_res = check_operation_name(func_name, normalized)
        if check_res:
            errors.extend(check_res)

        if not func_schema.get("description"):
            errors.append(
                f"{func_name} doesn't have a description. Python docstring is required for an API function.",
            )

    if warnings:
        for message in warnings:
            print(f"⚠️ Warn: {message}")
    if errors:
        for m in errors:
            print(f"❌ Error: {m}")
        os.abort()

    # === Convert each function ===
    for func_name, func_schema in functions.items():
        args_schema = fix_nullables(deepcopy(func_schema["properties"]["arguments"]))
        return_schema = fix_nullables(deepcopy(func_schema["properties"]["return"]))
        fix_error_refs(return_schema)

        args_schema = fix_empty_required(args_schema)
        return_schema = fix_empty_required(return_schema)
        # Register schemas under components
        args_name = make_schema_name(func_name, "args")
        return_name = make_schema_name(func_name, "return")
        openapi["components"]["schemas"][args_name] = args_schema  # type: ignore
        openapi["components"]["schemas"][return_name] = return_schema  # type: ignore
        tag = operation_to_tag(func_name)
        # Create a POST endpoint for the function
        openapi["paths"][f"/{func_name}"] = {  # type: ignore
            "post": {
                "summary": func_name,
                "operationId": func_name,
                "description": func_schema.get("description"),
                "tags": [tag],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{args_name}"},
                        },
                    },
                },
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": f"#/components/schemas/{return_name}",
                                },
                            },
                        },
                    },
                },
            },
        }

    sort_openapi_paths_by_tag_tree(openapi)

    # === Add global definitions from $defs ===
    for def_name, def_schema in defs.items():
        fixed_schema = fix_nullables(deepcopy(def_schema))
        fix_error_refs(fixed_schema)
        openapi["components"]["schemas"][def_name] = fixed_schema  # type: ignore

    # === Write to output JSON ===
    with Path("openapi.json").open("w") as f:
        json.dump(openapi, f, indent=2)

    print("✅ OpenAPI 3.0 JSON written to openapi.json")


if __name__ == "__main__":
    main()
