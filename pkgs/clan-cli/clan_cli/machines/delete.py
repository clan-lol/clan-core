import argparse
import shutil

from ..completions import add_dynamic_completer, complete_machines
from ..dirs import specific_machine_dir
from ..errors import ClanError


def delete_command(args: argparse.Namespace) -> None:
    folder = specific_machine_dir(args.flake, args.host)
    if folder.exists():
        shutil.rmtree(folder)
    else:
        raise ClanError(f"Machine {args.host} does not exist")


def register_delete_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument("host", type=str)
    add_dynamic_completer(machines_parser, complete_machines)

    parser.set_defaults(func=delete_command)
