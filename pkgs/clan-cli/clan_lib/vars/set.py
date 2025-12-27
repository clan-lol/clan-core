import logging
import sys

from clan_cli.vars.get import get_machine_var

from clan_lib.flake import Flake
from clan_lib.git import commit_files
from clan_lib.machines.machines import Machine
from clan_lib.vars.generator import Var
from clan_lib.vars.prompt import PromptType, ask

log = logging.getLogger(__name__)


def set_var(machine: str | Machine, var: str | Var, value: bytes, flake: Flake) -> None:
    if isinstance(machine, str):
        _machine = Machine(name=machine, flake=flake)
    else:
        _machine = machine
    _var = get_machine_var(_machine, var) if isinstance(var, str) else var
    paths = _var.set(value, _machine.name)
    if paths:
        commit_files(
            paths,
            _machine.flake_dir,
            f"Update var {_var.id} for machine {_machine.name}",
        )


def set_via_stdin(machine_name: str, var_id: str, flake: Flake) -> None:
    machine = Machine(name=machine_name, flake=flake)
    var = get_machine_var(machine, var_id)
    if sys.stdin.isatty():
        new_value = ask(
            var.id,
            PromptType.MULTILINE_HIDDEN,
            None,
            [machine_name],
        ).encode("utf-8")
    else:
        new_value = sys.stdin.buffer.read()

    set_var(machine, var, new_value, flake)
