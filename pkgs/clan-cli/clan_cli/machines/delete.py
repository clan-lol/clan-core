import argparse
import shutil

from ..api import API
from ..clan_uri import FlakeId
from ..completions import add_dynamic_completer, complete_machines
from ..dirs import specific_machine_dir
from ..errors import ClanError
from ..inventory import Inventory


@API.register
def delete_machine(flake: FlakeId, name: str) -> None:
    inventory = Inventory.load_file(flake.path)

    machine = inventory.machines.pop(name, None)
    if machine is None:
        raise ClanError(f"Machine {name} does not exist")

    inventory.persist(flake.path, f"Delete machine {name}")

    folder = specific_machine_dir(flake.path, name)
    if folder.exists():
        shutil.rmtree(folder)


def delete_command(args: argparse.Namespace) -> None:
    delete_machine(args.flake, args.name)


def register_delete_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument("name", type=str)
    add_dynamic_completer(machines_parser, complete_machines)

    parser.set_defaults(func=delete_command)
