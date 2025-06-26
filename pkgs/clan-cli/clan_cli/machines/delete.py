import argparse
import logging

from clan_lib.machines.delete import delete_machine
from clan_lib.machines.machines import Machine
from clan_lib.machines.suggestions import validate_machine_names

from clan_cli.completions import add_dynamic_completer, complete_machines

log = logging.getLogger(__name__)


def delete_command(args: argparse.Namespace) -> None:
    validate_machine_names([args.name], args.flake)
    delete_machine(Machine(flake=args.flake, name=args.name))


def register_delete_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument("name", type=str)
    add_dynamic_completer(machines_parser, complete_machines)

    parser.set_defaults(func=delete_command)
