import argparse
import logging

from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_lib.errors import ClanError
from clan_lib.flake import require_flake
from clan_lib.machines.machines import Machine
from clan_lib.vars.generator import Generator

log = logging.getLogger(__name__)


def fix_vars(machine: Machine, generator_name: None | str = None) -> None:
    generators = Generator.get_machine_generators([machine.name], machine.flake)
    if generator_name:
        for generator in generators:
            if generator_name == generator.name:
                generators = [generator]
                break
        else:
            err_msg = (
                f"Generator '{generator_name}' not found in machine {machine.name}"
            )
            raise ClanError(err_msg)

    machine.public_vars_store.fix(machine.name, generators=generators)
    machine.secret_vars_store.fix(machine.name, generators=generators)


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
