import argparse
from pathlib import Path

from ..errors import ClanError


def restore_backup(
    flake_dir: Path,
    machine: str,
    provider: str,
    backup_id: str,
    service: str | None = None,
) -> None:
    if service is None:
        print("would restore backup", machine, provider, backup_id)
    else:
        print(
            "would restore backup", machine, provider, backup_id, "of service:", service
        )


def restore_command(args: argparse.Namespace) -> None:
    if args.flake is None:
        raise ClanError("Could not find clan flake toplevel directory")
    restore_backup(
        Path(args.flake),
        machine=args.machine,
        provider=args.provider,
        backup_id=args.backup_id,
        service=args.service,
    )


def register_restore_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine", type=str, help="machine in the flake to create backups of"
    )
    parser.add_argument("provider", type=str, help="backup provider to use")
    parser.add_argument("backup_id", type=str, help="id of the backup to restore")
    parser.add_argument("--service", type=str, help="name of the service to restore")
    parser.set_defaults(func=restore_command)
