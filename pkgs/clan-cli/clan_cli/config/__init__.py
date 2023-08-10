# !/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Type, Union

import jsonschema

from clan_cli.errors import ClanError

script_dir = Path(__file__).parent


type_map: dict[str, type] = {
    "array": list,
    "boolean": bool,
    "integer": int,
    "number": float,
    "string": str,
}


class Kwargs:
    def __init__(self) -> None:
        self.type: Optional[Type] = None
        self.default: Any = None
        self.required: bool = False
        self.help: Optional[str] = None
        self.action: Optional[str] = None
        self.choices: Optional[list] = None


# A container inheriting from list, but overriding __contains__ to return True
# for all values.
# This is used to allow any value for the "choices" field of argparse
class AllContainer(list):
    def __contains__(self, item: Any) -> bool:
        return True


def schema_from_module_file(
    file: Union[str, Path] = f"{script_dir}/jsonschema/example-schema.json",
) -> dict[str, Any]:
    absolute_path = Path(file).absolute()
    # define a nix expression that loads the given module file using lib.evalModules
    nix_expr = f"""
        let
            lib = import <nixpkgs/lib>;
            slib = import {script_dir}/jsonschema {{inherit lib;}};
        in
            slib.parseModule {absolute_path}
    """
    # run the nix expression and parse the output as json
    return json.loads(
        subprocess.check_output(
            ["nix", "eval", "--impure", "--json", "--expr", nix_expr]
        )
    )


def options_types_from_schema(schema: dict[str, Any]) -> dict[str, Type]:
    result: dict[str, Type] = {}
    for name, value in schema.get("properties", {}).items():
        assert isinstance(value, dict)
        type_ = value["type"]
        if type_ == "object":
            # handle additionalProperties
            if "additionalProperties" in value:
                sub_type = value["additionalProperties"].get("type")
                if sub_type not in type_map:
                    raise ClanError(
                        f"Unsupported object type {sub_type} (field {name})"
                    )
                result[f"{name}.<name>"] = type_map[sub_type]
                continue
            # handle properties
            sub_result = options_types_from_schema(value)
            for sub_name, sub_type in sub_result.items():
                result[f"{name}.{sub_name}"] = sub_type
            continue
        elif type_ == "array":
            if "items" not in value:
                raise ClanError(f"Untyped arrays are not supported (field: {name})")
            sub_type = value["items"].get("type")
            if sub_type not in type_map:
                raise ClanError(f"Unsupported list type {sub_type} (field {name})")
            sub_type_: type = type_map[sub_type]
            result[name] = list[sub_type_]  # type: ignore
            continue
        result[name] = type_map[type_]
    return result


def process_args(args: argparse.Namespace, schema: dict) -> None:
    option = args.option
    value_arg = args.value

    option_path = option.split(".")
    # construct a nested dict from the option path and set the value
    result: dict[str, Any] = {}
    current = result
    for part in option_path[:-1]:
        current[part] = {}
        current = current[part]
    current[option_path[-1]] = value_arg

    # validate the result against the schema and cast the value to the expected type
    try:
        jsonschema.validate(result, schema)
    except jsonschema.ValidationError as e:
        schema_type = type_map[e.schema["type"]]
        # we use nargs="+", so we need to unwrap non-list values
        if isinstance(e.instance, list) and schema_type != list:
            instance_unwrapped = e.instance[0]
        else:
            instance_unwrapped = e.instance
        # try casting the value to the expected type
        try:
            value_casted = schema_type(instance_unwrapped)
        except TypeError:
            raise ClanError(
                f"Invalid value for {'.'.join(e.relative_path)}: {instance_unwrapped} (expected type: {schema_type})"
            ) from e
        current[option_path[-1]] = value_casted

    # print the result as json
    print(json.dumps(result, indent=2))


def register_parser(
    parser: argparse.ArgumentParser,
    file: Path = Path(f"{script_dir}/jsonschema/example-schema.json"),
) -> None:
    if file.name.endswith(".nix"):
        schema = schema_from_module_file(file)
    else:
        schema = json.loads(file.read_text())
    return _register_parser(parser, schema)


# takes a (sub)parser and configures it
def _register_parser(
    parser: Optional[argparse.ArgumentParser],
    schema: dict[str, Any],
) -> None:
    # check if schema is a .nix file and load it in that case
    if "type" not in schema:
        raise ClanError("Schema has no type")
    if schema["type"] != "object":
        raise ClanError("Schema is not an object")

    if parser is None:
        parser = argparse.ArgumentParser(description=schema.get("description"))

    # get all possible options from the schema
    options = options_types_from_schema(schema)

    # inject callback function to process the input later
    parser.set_defaults(func=lambda args: process_args(args, schema=schema))

    # add single positional argument for the option (e.g. "foo.bar")
    parser.add_argument(
        "option",
        # force this arg to be set
        nargs="?",
        help="Option to configure",
        type=str,
        choices=AllContainer(list(options.keys())),
    )

    # add a single optional argument for the value
    parser.add_argument(
        "value",
        # force this arg to be set
        nargs="+",
        help="Value to set",
    )


def main(argv: Optional[list[str]] = None) -> None:
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "schema",
        help="The schema to use for the configuration",
        type=Path,
    )
    args = parser.parse_args(argv[1:2])
    register_parser(parser, args.schema)
    parser.parse_args(argv[2:])


if __name__ == "__main__":
    main()
