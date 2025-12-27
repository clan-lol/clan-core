import argparse

from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_lib.flake import require_flake
from clan_lib.machines.machines import Machine
from clan_lib.vars.list import get_machine_vars


def list_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machine = Machine(name=args.machine, flake=flake)
    all_vars = get_machine_vars(machine)
    print("\n".join(sorted(str(var) for var in all_vars)))


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    machines_arg = parser.add_argument(
        "machine",
        help="The machine to print vars for",
    )
    add_dynamic_completer(machines_arg, complete_machines)

    parser.set_defaults(func=list_command)
