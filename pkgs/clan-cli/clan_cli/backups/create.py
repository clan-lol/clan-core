import argparse
import logging

from clan_lib.backups.create import create_backup
from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine

from clan_cli.completions import (
    add_dynamic_completer,
    complete_backup_providers_for_machine,
    complete_machines,
)

log = logging.getLogger(__name__)


def create_command(args: argparse.Namespace) -> None:
    if args.flake is None:
        msg = "Could not find clan flake toplevel directory"
        raise ClanError(msg)
    machine = Machine(name=args.machine, flake=args.flake)
    create_backup(machine=machine, provider=args.provider)


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machine", type=str, help="machine in the flake to create backups of"
    )
    add_dynamic_completer(machines_parser, complete_machines)

    provider_action = parser.add_argument(
        "--provider", type=str, help="backup provider to use"
    )
    add_dynamic_completer(provider_action, complete_backup_providers_for_machine)
    parser.set_defaults(func=create_command)
