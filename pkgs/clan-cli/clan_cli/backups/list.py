import argparse
import json
import subprocess
from dataclasses import dataclass

from ..errors import ClanError
from ..machines.machines import Machine


@dataclass
class Backup:
    archive_id: str
    date: str
    provider: str
    remote_path: str
    job_name: str


def list_provider(machine: Machine, provider: str) -> list[Backup]:
    results = []
    backup_metadata = json.loads(machine.eval_nix("config.clanCore.backups"))
    proc = machine.target_host.run(
        ["bash", "-c", backup_metadata["providers"][provider]["list"]],
        stdout=subprocess.PIPE,
        check=False,
    )
    if proc.returncode != 0:
        # TODO this should be a warning, only raise exception if no providers succeed
        ClanError(f"failed to list backups for provider {provider}")
    else:
        parsed_json = json.loads(proc.stdout)
        # TODO move borg specific code to borgbackup.nix
        for archive in parsed_json["archives"]:
            backup = Backup(
                archive_id=archive["archive"],
                date=archive["time"],
                provider=provider,
                remote_path=parsed_json["repository"]["location"],
                job_name=parsed_json["job-name"],
            )
            results.append(backup)
    return results


def list_backups(machine: Machine, provider: str | None = None) -> list[Backup]:
    backup_metadata = json.loads(machine.eval_nix("config.clanCore.backups"))
    results = []
    if provider is None:
        for _provider in backup_metadata["providers"]:
            results += list_provider(machine, _provider)

    else:
        results += list_provider(machine, provider)

    return results


def list_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)
    backups = list_backups(machine=machine, provider=args.provider)
    for backup in backups:
        print(backup.archive_id)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine", type=str, help="machine in the flake to show backups of"
    )
    parser.add_argument("--provider", type=str, help="backup provider to filter by")
    parser.set_defaults(func=list_command)
