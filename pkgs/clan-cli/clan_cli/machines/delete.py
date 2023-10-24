import argparse
import shutil

from ..dirs import specific_machine_dir
from ..errors import ClanError


def delete_command(args: argparse.Namespace) -> None:
    folder = specific_machine_dir(args.flake, args.host)
    if folder.exists():
        shutil.rmtree(folder)
    else:
        raise ClanError(f"Machine {args.host} does not exist")


def register_delete_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("host", type=str)
    parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to create machine for",
    )
    parser.set_defaults(func=delete_command)
