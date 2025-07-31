import argparse
import logging
from pathlib import Path

from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_lib.flake import Flake, require_flake
from clan_lib.machines.machines import Machine

from .generate import Var, get_generators

log = logging.getLogger(__name__)


def get_machine_vars(base_dir: str, machine_name: str) -> list[Var]:
    # TODO: We dont have machine level store / this granularity yet
    # We should move the store definition to the flake, as there can be only one store per clan
    machine = Machine(name=machine_name, flake=Flake(base_dir))
    pub_store = machine.public_vars_store
    sec_store = machine.secret_vars_store

    all_vars = []

    generators = get_generators(base_dir=Path(base_dir), machine_name=machine_name)
    for generator in generators:
        for var in generator.files:
            if var.secret:
                var.store(sec_store)
            else:
                var.store(pub_store)
            var.generator(generator)
            all_vars.append(var)
    return all_vars


def stringify_vars(_vars: list[Var]) -> str:
    return "\n".join([str(var) for var in _vars])


def stringify_all_vars(machine: Machine) -> str:
    return stringify_vars(get_machine_vars(str(machine.flake), machine.name))


def list_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machine = Machine(name=args.machine, flake=flake)
    print(stringify_all_vars(machine))


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    machines_arg = parser.add_argument(
        "machine",
        help="The machine to print vars for",
    )
    add_dynamic_completer(machines_arg, complete_machines)

    parser.set_defaults(func=list_command)
