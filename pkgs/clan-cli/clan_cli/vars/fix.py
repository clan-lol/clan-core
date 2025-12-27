import argparse

from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_lib.flake import require_flake
from clan_lib.machines.machines import Machine
from clan_lib.vars.fix import fix_vars


def fix_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machine = Machine(
        name=args.machine,
        flake=flake,
    )
    fix_vars(machine, generator_name=args.generator)


def register_fix_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machine",
        help="The machine to fix vars for",
    )
    add_dynamic_completer(machines_parser, complete_machines)

    parser.add_argument(
        "--generator",
        "-g",
        help="the generator to check",
    )
    parser.set_defaults(func=fix_command)
