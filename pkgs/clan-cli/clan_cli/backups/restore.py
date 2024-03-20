import argparse
import json
import subprocess

from ..errors import ClanError
from ..machines.machines import Machine


def restore_service(machine: Machine, name: str, provider: str, service: str) -> None:
    backup_metadata = json.loads(machine.eval_nix("config.clanCore.backups"))
    backup_folders = json.loads(machine.eval_nix("config.clanCore.state"))
    folders = backup_folders[service]["folders"]
    env = {}
    env["NAME"] = name
    env["FOLDERS"] = ":".join(folders)

    proc = machine.target_host.run(
        [backup_folders[service]["preRestoreScript"]],
        stdout=subprocess.PIPE,
        extra_env=env,
    )
    if proc.returncode != 0:
        raise ClanError(
            f"failed to run preRestoreScript: {backup_folders[service]['preRestoreScript']}, error was: {proc.stdout}"
        )

    proc = machine.target_host.run(
        [backup_metadata["providers"][provider]["restore"]],
        stdout=subprocess.PIPE,
        extra_env=env,
    )
    if proc.returncode != 0:
        raise ClanError(
            f"failed to restore backup: {backup_metadata['providers'][provider]['restore']}"
        )

    proc = machine.target_host.run(
        [backup_folders[service]["postRestoreScript"]],
        stdout=subprocess.PIPE,
        extra_env=env,
    )
    if proc.returncode != 0:
        raise ClanError(
            f"failed to run postRestoreScript: {backup_folders[service]['postRestoreScript']}, error was: {proc.stdout}"
        )


def restore_backup(
    machine: Machine,
    provider: str,
    name: str,
    service: str | None = None,
) -> None:
    if service is None:
        backup_folders = json.loads(machine.eval_nix("config.clanCore.state"))
        for _service in backup_folders:
            restore_service(machine, name, provider, _service)
    else:
        restore_service(machine, name, provider, service)


def restore_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)
    restore_backup(
        machine=machine,
        provider=args.provider,
        name=args.name,
        service=args.service,
    )


def register_restore_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine", type=str, help="machine in the flake to create backups of"
    )
    parser.add_argument("provider", type=str, help="backup provider to use")
    parser.add_argument("name", type=str, help="Name of the backup to restore")
    parser.add_argument("--service", type=str, help="name of the service to restore")
    parser.set_defaults(func=restore_command)
