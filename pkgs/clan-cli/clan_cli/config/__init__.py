# !/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional, Type

from clan_cli.errors import ClanError

script_dir = Path(__file__).parent


# nixos option type description to python type
def map_type(type: str) -> Type:
    if type == "boolean":
        return bool
    elif type in ["integer", "signed integer"]:
        return int
    elif type == "string":
        return str
    elif type.startswith("attribute set of"):
        subtype = type.removeprefix("attribute set of ")
        return dict[str, map_type(subtype)]  # type: ignore
    elif type.startswith("list of"):
        subtype = type.removeprefix("list of ")
        return list[map_type(subtype)]  # type: ignore
    else:
        raise ClanError(f"Unknown type {type}")


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


def process_args(option: str, value: Any, options: dict) -> None:
    option_path = option.split(".")

    # if the option cannot be found, then likely the type is attrs and we need to
    # find the parent option
    if option not in options:
        if len(option_path) == 1:
            raise ClanError(f"Option {option} not found")
        option_parent = option_path[:-1]
        attr = option_path[-1]
        return process_args(
            option=".".join(option_parent),
            value={attr: value},
            options=options,
        )

    target_type = map_type(options[option]["type"])

    # construct a nested dict from the option path and set the value
    result: dict[str, Any] = {}
    current = result
    for part in option_path[:-1]:
        current[part] = {}
        current = current[part]
    current[option_path[-1]] = value

    # value is always a list, as the arg parser cannot know the type upfront
    # and therefore always allows multiple arguments.
    def cast(value: Any, type: Type) -> Any:
        try:
            # handle bools
            if isinstance(type(), bool):
                if value == "true":
                    return True
                elif value == "false":
                    return False
                else:
                    raise ClanError(f"Invalid value {value} for boolean")
            # handle lists
            elif isinstance(type(), list):
                subtype = type.__args__[0]
                return [cast([x], subtype) for x in value]
            # handle dicts
            elif isinstance(type(), dict):
                if not isinstance(value, dict):
                    raise ClanError(
                        f"Cannot set {option} directly. Specify a suboption like {option}.<name>"
                    )
                subtype = type.__args__[1]
                return {k: cast(v, subtype) for k, v in value.items()}
            else:
                if len(value) > 1:
                    raise ClanError(f"Too many values for {option}")
                return type(value[0])
        except ValueError:
            raise ClanError(
                f"Invalid type for option {option} (expected {type.__name__})"
            )

    casted = cast(value, target_type)

    current[option_path[-1]] = casted

    # print the result as json
    print(json.dumps(result, indent=2))


def register_parser(
    parser: argparse.ArgumentParser,
    file: Path = Path(f"{script_dir}/jsonschema/options.json"),
) -> None:
    options = json.loads(file.read_text())
    return _register_parser(parser, options)


# takes a (sub)parser and configures it
def _register_parser(
    parser: Optional[argparse.ArgumentParser],
    options: dict[str, Any],
) -> None:
    if parser is None:
        parser = argparse.ArgumentParser(
            description="Set or show NixOS options",
        )

    # inject callback function to process the input later
    parser.set_defaults(
        func=lambda args: process_args(
            option=args.option, value=args.value, options=options
        )
    )

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
