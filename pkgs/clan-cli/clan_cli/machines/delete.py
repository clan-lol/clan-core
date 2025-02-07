import argparse
import logging
import shutil
from pathlib import Path

from clan_cli import inventory
from clan_cli.api import API
from clan_cli.clan_uri import Flake
from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_cli.dirs import specific_machine_dir
from clan_cli.secrets.folders import sops_secrets_folder
from clan_cli.secrets.machines import has_machine as secrets_has_machine
from clan_cli.secrets.machines import remove_machine as secrets_machine_remove
from clan_cli.secrets.secrets import (
    list_secrets,
)
from clan_cli.vars.list import (
    public_store as vars_public_store,
)
from clan_cli.vars.list import (
    secret_store as vars_secret_store,
)

from .machines import Machine

log = logging.getLogger(__name__)


@API.register
def delete_machine(flake: Flake, name: str) -> None:
    inventory.delete(str(flake.path), {f"machines.{name}"})

    changed_paths: list[Path] = []

    folder = specific_machine_dir(flake.path, name)
    if folder.exists():
        changed_paths.append(folder)
        shutil.rmtree(folder)

    # louis@(2025-02-04): clean-up legacy (pre-vars) secrets:
    sops_folder = sops_secrets_folder(flake.path)
    filter_fn = lambda secret_name: secret_name.startswith(f"{name}-")
    for secret_name in list_secrets(flake.path, filter_fn):
        secret_path = sops_folder / secret_name
        changed_paths.append(secret_path)
        shutil.rmtree(secret_path)

    machine = Machine(name, flake)
    changed_paths.extend(vars_public_store(machine).delete_store())
    changed_paths.extend(vars_secret_store(machine).delete_store())
    # Remove the machine's key, and update secrets & vars that referenced it:
    if secrets_has_machine(flake.path, name):
        secrets_machine_remove(flake.path, name)


def delete_command(args: argparse.Namespace) -> None:
    delete_machine(args.flake, args.name)


def register_delete_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument("name", type=str)
    add_dynamic_completer(machines_parser, complete_machines)

    parser.set_defaults(func=delete_command)
