import argparse
import sys

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_vars_for_machine,
)
from clan_lib.errors import ClanError
from clan_lib.flake import Flake, require_flake
from clan_lib.machines.machines import Machine
from clan_lib.vars.get import get_machine_var


def get_command(machine_name: str, var_id: str, flake: Flake) -> None:
    machine = Machine(name=machine_name, flake=flake)
    var = get_machine_var(machine, var_id)
    if not var.exists:
        msg = f"Var {var.id} has not been generated yet"
        raise ClanError(msg)
    if sys.stdout.isatty():
        sys.stdout.buffer.write(var.value)
    else:
        print(var.printable_value)


def _get_command(
    args: argparse.Namespace,
) -> None:
    flake = require_flake(args.flake)
    get_command(
        machine_name=args.machine,
        var_id=args.var_id,
        flake=flake,
    )


def register_get_parser(parser: argparse.ArgumentParser) -> None:
    machines_arg = parser.add_argument(
        "machine",
        help="The machine to print vars for",
    )
    add_dynamic_completer(machines_arg, complete_machines)

    var_id_arg = parser.add_argument(
        "var_id",
        help="The var id to get the value for. Example: ssh-keys/pubkey",
    )
    add_dynamic_completer(var_id_arg, complete_vars_for_machine)

    parser.set_defaults(func=_get_command)
