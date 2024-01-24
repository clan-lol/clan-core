import argparse
import json
import os
import subprocess

from ..errors import ClanError
from ..machines.machines import Machine
from .list import Backup, list_backups


def restore_service(
    machine: Machine, backup: Backup, provider: str, service: str
) -> None:
    backup_metadata = json.loads(machine.eval_nix("config.clanCore.backups"))
    backup_folders = json.loads(machine.eval_nix("config.clanCore.state"))
    folders = backup_folders[service]["folders"]
    env = os.environ.copy()
    env["ARCHIVE_ID"] = backup.archive_id
    env["LOCATION"] = backup.remote_path
    env["JOB"] = backup.job_name
    env["FOLDERS"] = ":".join(folders)

    proc = machine.host.run(
        [
            "bash",
            "-c",
            backup_folders[service]["preRestoreScript"],
        ],
        stdout=subprocess.PIPE,
        extra_env=env,
    )
    if proc.returncode != 0:
        raise ClanError(
            f"failed to run preRestoreScript: {backup_folders[service]['preRestoreScript']}, error was: {proc.stdout}"
        )

    proc = machine.host.run(
        [
            "bash",
            "-c",
            backup_metadata["providers"][provider]["restore"],
        ],
        stdout=subprocess.PIPE,
        extra_env=env,
    )
    if proc.returncode != 0:
        raise ClanError(
            f"failed to restore backup: {backup_metadata['providers'][provider]['restore']}"
        )

    proc = machine.host.run(
        [
            "bash",
            "-c",
            backup_folders[service]["postRestoreScript"],
        ],
        stdout=subprocess.PIPE,
        extra_env=env,
    )
    if proc.returncode != 0:
        raise ClanError(
            f"failed to run postRestoreScript: {backup_folders[service]['postRestoreScript']}, error was: {proc.stdout}"
        )


def restore_backup(
    machine: Machine,
    backups: list[Backup],
    provider: str,
    archive_id: str,
    service: str | None = None,
) -> None:
    if service is None:
        for backup in backups:
            if backup.archive_id == archive_id:
                backup_folders = json.loads(machine.eval_nix("config.clanCore.state"))
                for _service in backup_folders:
                    restore_service(machine, backup, provider, _service)
    else:
        for backup in backups:
            if backup.archive_id == archive_id:
                restore_service(machine, backup, provider, service)


def restore_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)
    backups = list_backups(machine=machine, provider=args.provider)
    restore_backup(
        machine=machine,
        backups=backups,
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
