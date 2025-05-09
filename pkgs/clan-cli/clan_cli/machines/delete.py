import argparse
import logging
import shutil
from pathlib import Path

from clan_lib.api import API

from clan_cli import inventory
from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_cli.dirs import specific_machine_dir
from clan_cli.machines.machines import Machine
from clan_cli.secrets.folders import sops_secrets_folder
from clan_cli.secrets.machines import has_machine as secrets_has_machine
from clan_cli.secrets.machines import remove_machine as secrets_machine_remove
from clan_cli.secrets.secrets import (
    list_secrets,
)

log = logging.getLogger(__name__)


@API.register
def delete_machine(machine: Machine) -> None:
    try:
        inventory.delete(machine.flake, {f"machines.{machine.name}"})
    except KeyError as exc:
        # louis@(2025-03-09): test infrastructure does not seem to set the
        # inventory properly, but more importantly only one machine in my
        # personal clan ended up in the inventory for some reason, so I think
        # it makes sense to eat the exception here.
        log.warning(
            f"{machine.name} was missing or already deleted from the machines inventory: {exc}"
        )

    changed_paths: list[Path] = []

    folder = specific_machine_dir(machine)
    if folder.exists():
        changed_paths.append(folder)
        shutil.rmtree(folder)

    # louis@(2025-02-04): clean-up legacy (pre-vars) secrets:
    sops_folder = sops_secrets_folder(machine.flake.path)
    filter_fn = lambda secret_name: secret_name.startswith(f"{machine.name}-")
    for secret_name in list_secrets(machine.flake.path, filter_fn):
        secret_path = sops_folder / secret_name
        changed_paths.append(secret_path)
        shutil.rmtree(secret_path)

    changed_paths.extend(machine.public_vars_store.delete_store())
    changed_paths.extend(machine.secret_vars_store.delete_store())
    # Remove the machine's key, and update secrets & vars that referenced it:
    if secrets_has_machine(machine.flake.path, machine.name):
        secrets_machine_remove(machine.flake.path, machine.name)


def delete_command(args: argparse.Namespace) -> None:
    delete_machine(Machine(flake=args.flake, name=args.name))


def register_delete_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument("name", type=str)
    add_dynamic_completer(machines_parser, complete_machines)

    parser.set_defaults(func=delete_command)
