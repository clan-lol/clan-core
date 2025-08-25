import argparse

from clan_lib.backups.restore import restore_backup
from clan_lib.flake import require_flake
from clan_lib.machines.machines import Machine

from clan_cli.completions import (
    add_dynamic_completer,
    complete_backup_providers_for_machine,
    complete_machines,
)


def restore_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machine = Machine(name=args.machine, flake=flake)
    restore_backup(
        machine=machine,
        provider=args.provider,
        name=args.name,
        service=args.service,
    )


def register_restore_parser(parser: argparse.ArgumentParser) -> None:
    machine_action = parser.add_argument(
        "machine",
        type=str,
        help="machine in the flake to create backups of",
    )
    add_dynamic_completer(machine_action, complete_machines)
    provider_action = parser.add_argument(
        "provider",
        type=str,
        help="backup provider to use",
    )
    add_dynamic_completer(provider_action, complete_backup_providers_for_machine)
    parser.add_argument("name", type=str, help="Name of the backup to restore")
    parser.add_argument("--service", type=str, help="name of the service to restore")
    parser.set_defaults(func=restore_command)
