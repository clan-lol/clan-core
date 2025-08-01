import argparse
import logging
import sys

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_vars_for_machine,
)
from clan_cli.vars.get import get_machine_var
from clan_cli.vars.prompt import PromptType
from clan_lib.flake import Flake
from clan_lib.git import commit_files
from clan_lib.machines.machines import Machine

from .generate import Var
from .prompt import ask

log = logging.getLogger(__name__)


def set_var(machine: str | Machine, var: str | Var, value: bytes, flake: Flake) -> None:
    if isinstance(machine, str):
        _machine = Machine(name=machine, flake=flake)
    else:
        _machine = machine
    if isinstance(var, str):
        _var = get_machine_var(str(flake.path), _machine.name, var)
    else:
        _var = var
    path = _var.set(value)
    if path:
        commit_files(
            [path],
            _machine.flake_dir,
            f"Update var {_var.id} for machine {_machine.name}",
        )


def set_via_stdin(machine_name: str, var_id: str, flake: Flake) -> None:
    machine = Machine(name=machine_name, flake=flake)
    var = get_machine_var(str(flake.path), machine_name, var_id)
    if sys.stdin.isatty():
        new_value = ask(
            var.id,
            PromptType.MULTILINE_HIDDEN,
            None,
        ).encode("utf-8")
    else:
        new_value = sys.stdin.buffer.read()

    set_var(machine, var, new_value, flake)


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
