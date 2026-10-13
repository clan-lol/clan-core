import argparse

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_vars_for_machine,
)
from clan_lib.errors import ClanError
from clan_lib.flake import Flake, require_flake
from clan_lib.machines.machines import Machine
from clan_lib.vars.get import get_machine_var
from clan_lib.vars.set import set_var


def cp_command(
    src_machine_name: str, dest_machine_name: str, var_id: str, flake: Flake
) -> None:
    src_machine = Machine(name=src_machine_name, flake=flake)
    dest_machine = Machine(name=dest_machine_name, flake=flake)

    var = get_machine_var(src_machine, var_id)

    if not var.exists:
        msg = f"Var {var.id} has not yet been generated for source machine {src_machine_name}"
        raise ClanError(msg)

    # use var_id because set_var ignores the machine argument if passed an already-resolved var
    set_var(dest_machine, var_id, var.value, flake)


def _cp_command(
    args: argparse.Namespace,
) -> None:
    flake = require_flake(args.flake)
    cp_command(
        src_machine_name=args.source_machine,
        dest_machine_name=args.destination_machine,
        var_id=args.var_id,
        flake=flake,
    )


def register_cp_parser(parser: argparse.ArgumentParser) -> None:
    source_machines_arg = parser.add_argument(
        "source_machine",
        help="The machine to get the var from",
    )
    add_dynamic_completer(source_machines_arg, complete_machines)

    target_machines_arg = parser.add_argument(
        "destination_machine",
        help="The machine to set the var for",
    )
    add_dynamic_completer(target_machines_arg, complete_machines)

    var_id_arg = parser.add_argument(
        "var_id",
        help="The var id for which to set the value. Example: ssh-keys/pubkey",
    )
    add_dynamic_completer(var_id_arg, complete_vars_for_machine)

    parser.set_defaults(func=_cp_command)
