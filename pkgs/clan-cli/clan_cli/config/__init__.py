# !/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional, Type

from clan_cli.errors import ClanError

from . import parsing

script_dir = Path(__file__).parent


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
    schema_type = parsing.type_from_schema_path(schema, option_path)

    # we use nargs="+", so we need to unwrap non-list values
    if isinstance(schema_type(), list):
        subtype = schema_type.__args__[0]
        casted = [subtype(x) for x in value_arg]
    elif isinstance(schema_type(), dict):
        subtype = schema_type.__args__[1]
        raise ClanError("Dicts are not supported")
    else:
        casted = schema_type(value_arg[0])

    current[option_path[-1]] = casted

    # print the result as json
    print(json.dumps(result, indent=2))


def register_parser(
    parser: argparse.ArgumentParser,
    file: Path = Path(f"{script_dir}/jsonschema/example-schema.json"),
) -> None:
    if file.name.endswith(".nix"):
        schema = parsing.schema_from_module_file(file)
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
    options = parsing.options_types_from_schema(schema)

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
