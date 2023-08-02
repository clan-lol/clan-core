# !/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Union


class Kwargs:
    def __init__(self):
        self.type = None
        self.default: Any = None
        self.required: bool = False
        self.help: Optional[str] = None
        self.action: Optional[str] = None
        self.choices: Optional[list] = None


def schema_from_module_file(
    file: Union[str, Path] = "./tests/config/example-interface.nix",
) -> dict:
    absolute_path = Path(file).absolute()
    # define a nix expression that loads the given module file using lib.evalModules
    nix_expr = f"""
        let
            lib = import <nixpkgs/lib>;
            slib = import {__file__}/../schema-lib.nix {{inherit lib;}};
        in
            slib.parseModule {absolute_path}
    """
    # run the nix expression and parse the output as json
    return json.loads(
        subprocess.check_output(
            ["nix", "eval", "--impure", "--json", "--expr", nix_expr]
        )
    )


# takes a (sub)parser and configures it
def register_parser(
    parser: Optional[argparse.ArgumentParser] = None,
    schema: Union[dict, str, Path] = "./tests/config/example-interface.nix",
) -> dict:
    # check if schema is a .nix file and load it in that case
    if isinstance(schema, str) and schema.endswith(".nix"):
        schema = schema_from_module_file(schema)
    elif not isinstance(schema, dict):
        with open(str(schema)) as f:
            schema: dict = json.load(f)
    assert "type" in schema and schema["type"] == "object"

    required_set = set(schema.get("required", []))

    type_map = {
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

        # TODO: add support for nested objects
        if value.get("type") == "object":
            subparser = subparsers.add_parser(name, help=value.get("description"))
            register_parser(parser=subparser, schema=value)
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
            assert len(enum_list) > 0, "Enum List is Empty"
            arg_type = type(enum_list[0])
            assert all(
                arg_type is type(item) for item in enum_list
            ), f"Items in [{enum_list}] with Different Types"

            kwargs.type = arg_type
            kwargs.choices = enum_list
        else:
            kwargs.type = type_map[value.get("type")]
            del kwargs.choices

        name = f"--{name}"

        if kwargs.type is bool:
            assert not kwargs.default, "boolean have to be False in default"
            kwargs.default = False
            kwargs.action = "store_true"
            del kwargs.type
        else:
            del kwargs.action

        parser.add_argument(name, **vars(kwargs))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "schema",
        help="The schema to use for the configuration",
        type=str,
    )
    args = parser.parse_args(sys.argv[1:2])
    schema = args.schema
    register_parser(schema=schema, parser=parser)
    parser.parse_args(sys.argv[2:])


if __name__ == "__main__":
    main()
