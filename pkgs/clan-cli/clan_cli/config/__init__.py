# !/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Type, Union

from clan_cli.errors import ClanError

script_dir = Path(__file__).parent


# nixos option type description to python type
def map_type(type: str) -> Type:
    if type == "boolean":
        return bool
    elif type in [
        "integer",
        "signed integer",
        "16 bit unsigned integer; between 0 and 65535 (both inclusive)",
    ]:
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


# merge two dicts recursively
def merge(a: dict, b: dict, path: list[str] = []) -> dict:
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            elif isinstance(a[key], list) and isinstance(b[key], list):
                a[key].extend(b[key])
            elif a[key] != b[key]:
                raise Exception("Conflict at " + ".".join(path + [str(key)]))
        else:
            a[key] = b[key]
    return a


# A container inheriting from list, but overriding __contains__ to return True
# for all values.
# This is used to allow any value for the "choices" field of argparse
class AllContainer(list):
    def __contains__(self, item: Any) -> bool:
        return True


# value is always a list, as the arg parser cannot know the type upfront
# and therefore always allows multiple arguments.
def cast(value: Any, type: Type, opt_description: str) -> Any:
    try:
        # handle bools
        if isinstance(type(), bool):
            if value[0] in ["true", "True", "yes", "y", "1"]:
                return True
            elif value[0] in ["false", "False", "no", "n", "0"]:
                return False
            else:
                raise ClanError(f"Invalid value {value} for boolean")
        # handle lists
        elif isinstance(type(), list):
            subtype = type.__args__[0]
            return [cast([x], subtype, opt_description) for x in value]
        # handle dicts
        elif isinstance(type(), dict):
            if not isinstance(value, dict):
                raise ClanError(
                    f"Cannot set {opt_description} directly. Specify a suboption like {opt_description}.<name>"
                )
            subtype = type.__args__[1]
            return {k: cast(v, subtype, opt_description) for k, v in value.items()}
        else:
            if len(value) > 1:
                raise ClanError(f"Too many values for {opt_description}")
            return type(value[0])
    except ValueError:
        raise ClanError(
            f"Invalid type for option {opt_description} (expected {type.__name__})"
        )


def process_args(
    option: str, value: Any, options: dict, option_description: str = ""
) -> None:
    option_path = option.split(".")

    # if the option cannot be found, then likely the type is attrs and we need to
    # find the parent option
    if option not in options:
        if len(option_path) == 1:
            raise ClanError(f"Option {option_description} not found")
        option_parent = option_path[:-1]
        attr = option_path[-1]
        return process_args(
            option=".".join(option_parent),
            value={attr: value},
            options=options,
            option_description=option,
        )

    target_type = map_type(options[option]["type"])

    # construct a nested dict from the option path and set the value
    result: dict[str, Any] = {}
    current = result
    for part in option_path[:-1]:
        current[part] = {}
        current = current[part]
    current[option_path[-1]] = value

    casted = cast(value, target_type, option)

    current[option_path[-1]] = casted

    # check if there is an existing config file
    if os.path.exists("clan-settings.json"):
        with open("clan-settings.json") as f:
            current_config = json.load(f)
    else:
        current_config = {}
    # merge and save the new config file
    new_config = merge(current_config, result)
    with open("clan-settings.json", "w") as f:
        json.dump(new_config, f, indent=2)
    print("New config:")
    print(json.dumps(new_config, indent=2))


def register_parser(
    parser: argparse.ArgumentParser,
    optionsFile: Optional[Union[str, Path]] = os.environ.get("CLAN_OPTIONS_FILE"),
) -> None:
    if not optionsFile:
        # use nix eval to evaluate .#clanOptions
        # this will give us the evaluated config with the options attribute
        proc = subprocess.run(
            [
                "nix",
                "eval",
                "--raw",
                ".#clanOptions",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        file = proc.stdout.strip()
        with open(file) as f:
            options = json.load(f)
    else:
        with open(optionsFile) as f:
            options = json.load(f)
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
