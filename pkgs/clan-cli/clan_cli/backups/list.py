import argparse
import json
import subprocess
from typing import Any

from ..errors import ClanError
from ..machines.machines import Machine


def list_backups(machine: Machine, provider: str | None = None) -> list[dict[str, Any]]:
    backup_scripts = json.loads(
        machine.eval_nix(f"nixosConfigurations.{machine.name}.config.clanCore.backups")
    )
    results = []
    if provider is None:
        for provider in backup_scripts["providers"]:
            proc = subprocess.run(
                ["bash", "-c", backup_scripts["providers"][provider]["list"]],
                stdout=subprocess.PIPE,
            )
            if proc.returncode != 0:
                # TODO this should be a warning, only raise exception if no providers succeed
                raise ClanError("failed to list backups")
            else:
                results.append(proc.stdout)
    else:
        if provider not in backup_scripts["providers"]:
            raise ClanError(f"provider {provider} not found")
        proc = subprocess.run(
            ["bash", "-c", backup_scripts["providers"][provider]["list"]],
            stdout=subprocess.PIPE,
        )
        if proc.returncode != 0:
            raise ClanError("failed to list backup")
        else:
            results.append(proc.stdout)

    return list(map(json.loads, results))


def list_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake_dir=args.flake)
    backups_data = list_backups(machine=machine, provider=args.provider)
    print(json.dumps(list(backups_data)))


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine", type=str, help="machine in the flake to show backups of"
    )
    parser.add_argument("--provider", type=str, help="backup provider to filter by")
    parser.set_defaults(func=list_command)
