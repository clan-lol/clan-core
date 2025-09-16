import argparse
import logging
import sys

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_vars_for_machine,
)
from clan_lib.errors import ClanError
from clan_lib.flake import Flake, require_flake
from clan_lib.machines.machines import Machine

from .generator import Var
from .list import get_machine_vars

log = logging.getLogger(__name__)


def get_machine_var(machine: Machine, var_id: str) -> Var:
    log.debug(f"getting var: {var_id} from machine: {machine.name}")
    vars_ = get_machine_vars(machine)
    results = []
    for var in vars_:
        if var.id == var_id:
            # exact match
            results = [var]
            break
        if var.id.startswith(var_id):
            results.append(var)
    if len(results) == 0:
        msg = f"Couldn't find var: {var_id} for machine: {machine}"
        raise ClanError(msg)
    if len(results) > 1:
        error = f"Found multiple vars in {machine} for {var_id}:\n  - " + "\n  - ".join(
            [str(var) for var in results],
        )
        raise ClanError(error)
    # we have exactly one result at this point
    var = results[0]
    if var_id == var.id:
        return var
    msg = f"Did you mean: {var.id}"
    raise ClanError(msg)


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
