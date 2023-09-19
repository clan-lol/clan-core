# !/usr/bin/env python3
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional, Type

from clan_cli.dirs import get_clan_flake_toplevel
from clan_cli.errors import ClanError
from clan_cli.machines.folders import machine_settings_file
from clan_cli.nix import nix_eval

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
                a[key] = b[key]
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


def options_for_machine(machine_name: str, flake: Optional[Path] = None) -> dict:
    if flake is None:
        flake = get_clan_flake_toplevel()
    # use nix eval to lib.evalModules .#clanModules.machine-{machine_name}
    proc = subprocess.run(
        nix_eval(
            flags=[
                "--show-trace",
                "--impure",
                "--expr",
                f"""
                let
                    flake = builtins.getFlake (toString {flake});
                    lib = flake.inputs.nixpkgs.lib;
                    options = flake.nixosConfigurations.{machine_name}.options;

                    # this is actually system independent as it uses toFile
                    docs = flake.inputs.nixpkgs.legacyPackages.x86_64-linux.nixosOptionsDoc {{
                        inherit options;
                    }};
                    opts = builtins.fromJSON (builtins.readFile docs.optionsJSON.options);
            in
                opts
                """,
            ],
        ),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise Exception(
            f"Failed to read options for machine {machine_name}:\n{proc.stderr}"
        )
    options = json.loads(proc.stdout)
    return options


def read_machine_option_value(machine_name: str, option: str) -> str:
    # use nix eval to read from .#nixosConfigurations.default.config.{option}
    # this will give us the evaluated config with the options attribute
    proc = subprocess.run(
        nix_eval(
            flags=[
                "--show-trace",
                "--extra-experimental-features",
                "nix-command flakes",
                f".#nixosConfigurations.{machine_name}.config.{option}",
            ],
        ),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise ClanError(f"Failed to read option {option}:\n{proc.stderr}")
    value = json.loads(proc.stdout)
    # print the value so that the output can be copied and fed as an input.
    # for example a list should be displayed as space separated values surrounded by quotes.
    if isinstance(value, list):
        out = " ".join([json.dumps(x) for x in value])
    elif isinstance(value, dict):
        out = json.dumps(value, indent=2)
    else:
        out = json.dumps(value, indent=2)
    return out


def get_or_set_option(args: argparse.Namespace) -> None:
    if args.value == []:
        print(read_machine_option_value(args.machine, args.option))
    else:
        # load options
        if args.options_file is None:
            options = options_for_machine(machine_name=args.machine)
        else:
            with open(args.options_file) as f:
                options = json.load(f)
        # compute settings json file location
        if args.settings_file is None:
            get_clan_flake_toplevel()
            settings_file = machine_settings_file(args.machine)
        else:
            settings_file = args.settings_file
        # set the option with the given value
        set_option(
            option=args.option,
            value=args.value,
            options=options,
            settings_file=settings_file,
            option_description=args.option,
        )
        if not args.quiet:
            new_value = read_machine_option_value(args.machine, args.option)
            print(f"New Value for {args.option}:")
            print(new_value)


def set_option(
    option: str,
    value: Any,
    options: dict,
    settings_file: Path,
    option_description: str = "",
) -> None:
    option_path = option.split(".")

    # if the option cannot be found, then likely the type is attrs and we need to
    # find the parent option.
    if option not in options:
        if len(option_path) == 1:
            raise ClanError(f"Option {option_description} not found")
        option_parent = option_path[:-1]
        attr = option_path[-1]
        return set_option(
            option=".".join(option_parent),
            value={attr: value},
            options=options,
            settings_file=settings_file,
            option_description=option,
        )

    target_type = map_type(options[option]["type"])
    casted = cast(value, target_type, option)

    # construct a nested dict from the option path and set the value
    result: dict[str, Any] = {}
    current = result
    for part in option_path[:-1]:
        current[part] = {}
        current = current[part]
    current[option_path[-1]] = value

    current[option_path[-1]] = casted

    # check if there is an existing config file
    if os.path.exists(settings_file):
        with open(settings_file) as f:
            current_config = json.load(f)
    else:
        current_config = {}
    # merge and save the new config file
    new_config = merge(current_config, result)
    settings_file.parent.mkdir(parents=True, exist_ok=True)
    with open(settings_file, "w") as f:
        json.dump(new_config, f, indent=2)


# takes a (sub)parser and configures it
def register_parser(
    parser: Optional[argparse.ArgumentParser],
) -> None:
    if parser is None:
        parser = argparse.ArgumentParser(
            description="Set or show NixOS options",
        )

    # inject callback function to process the input later
    parser.set_defaults(func=get_or_set_option)

    # add --machine argument
    parser.add_argument(
        "--machine",
        "-m",
        help="Machine to configure",
        type=str,
        default="default",
    )

    # add --options-file argument
    parser.add_argument(
        "--options-file",
        help="JSON file with options",
        type=Path,
    )

    # add --settings-file argument
    parser.add_argument(
        "--settings-file",
        help="JSON file with settings",
        type=Path,
    )
    # add --quiet argument
    parser.add_argument(
        "--quiet",
        help="Do not print the value",
        action="store_true",
    )

    # add single positional argument for the option (e.g. "foo.bar")
    parser.add_argument(
        "option",
        help="Option to read or set",
        type=str,
    )

    # add a single optional argument for the value
    parser.add_argument(
        "value",
        # force this arg to be set
        nargs="*",
        help="Value to set",
    )


def main(argv: Optional[list[str]] = None) -> None:
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser()
    register_parser(parser)
    parser.parse_args(argv[1:])


if __name__ == "__main__":
    main()
