import argparse

from clan_lib.backups.list import list_backups
from clan_lib.flake import require_flake
from clan_lib.machines.machines import Machine

from clan_cli.completions import (
    add_dynamic_completer,
    complete_backup_providers_for_machine,
    complete_machines,
)


def list_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machine = Machine(name=args.machine, flake=flake)
    backups = list_backups(machine=machine, provider=args.provider)
    for backup in backups:
        print(backup.name)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machine", type=str, help="machine in the flake to show backups of"
    )
    add_dynamic_completer(machines_parser, complete_machines)
    provider_action = parser.add_argument(
        "--provider", type=str, help="backup provider to filter by"
    )
    add_dynamic_completer(provider_action, complete_backup_providers_for_machine)
    parser.set_defaults(func=list_command)
