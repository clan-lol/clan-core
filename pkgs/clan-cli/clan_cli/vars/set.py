import argparse

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_vars_for_machine,
)
from clan_lib.vars.set import set_via_stdin


def _set_command(args: argparse.Namespace) -> None:
    set_via_stdin(args.machine, args.var_id, args.flake)


def register_set_parser(parser: argparse.ArgumentParser) -> None:
    machines_arg = parser.add_argument(
        "machine",
        help="The machine to set a var for",
    )
    add_dynamic_completer(machines_arg, complete_machines)

    var_id_arg = parser.add_argument(
        "var_id",
        help="The var id for which to set the value. Example: ssh-keys/pubkey",
    )
    add_dynamic_completer(var_id_arg, complete_vars_for_machine)

    parser.set_defaults(func=_set_command)
