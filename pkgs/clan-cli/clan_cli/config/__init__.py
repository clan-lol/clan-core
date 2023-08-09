# !/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Type, Union

from clan_cli.errors import ClanError

script_dir = Path(__file__).parent


class Kwargs:
    def __init__(self) -> None:
        self.type: Optional[Type] = None
        self.default: Any = None
        self.required: bool = False
        self.help: Optional[str] = None
        self.action: Optional[str] = None
        self.choices: Optional[list] = None


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

    required_set = set(schema.get("required", []))

    type_map: dict[str, Type] = {
        "array": list,
        "boolean": bool,
        "integer": int,
        "number": float,
        "string": str,
    }

    if parser is None:
        parser = argparse.ArgumentParser(description=schema.get("description"))

    subparsers = parser.add_subparsers(
        title="more options",
        description="Other options to configure",
        help="the option to configure",
        required=True,
    )

    for name, value in schema.get("properties", {}).items():
        assert isinstance(value, dict)
        type_ = value.get("type")

        # TODO: add support for nested objects
        if type_ == "object":
            subparser = subparsers.add_parser(name, help=value.get("description"))
            _register_parser(parser=subparser, schema=value)
            continue
        # elif value.get("type") == "array":
        #     subparser = parser.add_subparsers(dest=name)
        #     register_parser(subparser, value)
        #     continue
        kwargs = Kwargs()
        kwargs.default = value.get("default")
        kwargs.help = value.get("description")
        kwargs.required = name in required_set

        if kwargs.default is not None:
            kwargs.help = f"{kwargs.help}, [{kwargs.default}] in default"

        if "enum" in value:
            enum_list = value["enum"]
            if len(enum_list) == 0:
                raise ClanError("Enum List is Empty")
            arg_type = type(enum_list[0])
            if not all(arg_type is type(item) for item in enum_list):
                raise ClanError(f"Items in [{enum_list}] with Different Types")

            kwargs.type = arg_type
            kwargs.choices = enum_list
        elif type_ in type_map:
            kwargs.type = type_map[type_]
            del kwargs.choices
        else:
            raise ClanError(f"Unsupported Type '{type_}' in schema")

        name = f"--{name}"

        if kwargs.type is bool:
            if kwargs.default:
                raise ClanError("Boolean have to be False in default")
            kwargs.default = False
            kwargs.action = "store_true"
            del kwargs.type
        else:
            del kwargs.action

        parser.add_argument(name, **vars(kwargs))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "schema",
        help="The schema to use for the configuration",
        type=str,
    )
    args = parser.parse_args(sys.argv[1:2])
    register_parser(parser, args.schema)
    parser.parse_args(sys.argv[2:])


if __name__ == "__main__":
    main()
