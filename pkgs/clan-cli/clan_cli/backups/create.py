import argparse
import json
import logging

from ..errors import ClanError
from ..machines.machines import Machine

log = logging.getLogger(__name__)


def create_backup(machine: Machine, provider: str | None = None) -> None:
    log.info(f"creating backup for {machine.name}")
    backup_scripts = json.loads(machine.eval_nix("config.clanCore.backups"))
    if provider is None:
        for provider in backup_scripts["providers"]:
            proc = machine.target_host.run(
                [backup_scripts["providers"][provider]["create"]],
            )
            if proc.returncode != 0:
                raise ClanError("failed to start backup")
            else:
                print("successfully started backup")
    else:
        if provider not in backup_scripts["providers"]:
            raise ClanError(f"provider {provider} not found")
        proc = machine.target_host.run(
            [backup_scripts["providers"][provider]["create"]],
        )
        if proc.returncode != 0:
            raise ClanError("failed to start backup")
        else:
            print("successfully started backup")


def create_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)
    create_backup(machine=machine, provider=args.provider)


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine", type=str, help="machine in the flake to create backups of"
    )
    parser.add_argument("--provider", type=str, help="backup provider to use")
    parser.set_defaults(func=create_command)
