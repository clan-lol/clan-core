import argparse
import json
import os
import subprocess
from typing import Any

from ..errors import ClanError
from ..machines.machines import Machine
from .list import list_backups


def restore_backup(
    backup_data: list[dict[str, Any]],
    machine: Machine,
    provider: str,
    archive_id: str,
    service: str | None = None,
) -> None:
    backup_scripts = json.loads(
        machine.eval_nix(f"nixosConfigurations.{machine.name}.config.clanCore.backups")
    )
    backup_folders = json.loads(
        machine.eval_nix(f"nixosConfigurations.{machine.name}.config.clanCore.state")
    )
    if service is None:
        for backup in backup_data:
            for archive in backup["archives"]:
                if archive["archive"] == archive_id:
                    env = os.environ.copy()
                    env["ARCHIVE_ID"] = archive_id
                    env["LOCATION"] = backup["repository"]["location"]
                    env["JOB"] = backup["job-name"]
                    proc = subprocess.run(
                        [
                            "bash",
                            "-c",
                            backup_scripts["providers"][provider]["restore"],
                        ],
                        stdout=subprocess.PIPE,
                        env=env,
                    )
                    if proc.returncode != 0:
                        # TODO this should be a warning, only raise exception if no providers succeed
                        raise ClanError("failed to restore backup")
    else:
        print(
            "would restore backup",
            machine,
            provider,
            archive_id,
            "of service:",
            service,
        )
        print(backup_folders)


def restore_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake_dir=args.flake)
    backup_data = list_backups(machine=machine, provider=args.provider)
    restore_backup(
        backup_data=backup_data,
        machine=machine,
        provider=args.provider,
        archive_id=args.archive_id,
        service=args.service,
    )


def register_restore_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine", type=str, help="machine in the flake to create backups of"
    )
    parser.add_argument("provider", type=str, help="backup provider to use")
    parser.add_argument("archive_id", type=str, help="id of the backup to restore")
    parser.add_argument("--service", type=str, help="name of the service to restore")
    parser.set_defaults(func=restore_command)
