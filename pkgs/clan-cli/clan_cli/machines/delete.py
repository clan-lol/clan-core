import argparse
import shutil
from pathlib import Path

from clan_cli.api import API
from clan_cli.inventory import Inventory

from ..completions import add_dynamic_completer, complete_machines
from ..dirs import specific_machine_dir
from ..errors import ClanError


@API.register
def delete_machine(base_dir: str | Path, name: str) -> None:
    inventory = Inventory.load_file(base_dir)

    machine = inventory.machines.pop(name, None)
    if machine is None:
        raise ClanError(f"Machine {name} does not exist")

    inventory.persist(base_dir)

    folder = specific_machine_dir(Path(base_dir), name)
    if folder.exists():
        shutil.rmtree(folder)


def delete_command(args: argparse.Namespace) -> None:
    delete_machine(args.flake, args.name)


def register_delete_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument("name", type=str)
    add_dynamic_completer(machines_parser, complete_machines)

    parser.set_defaults(func=delete_command)
