import argparse
import shutil

from ..errors import ClanError
from .folders import machine_folder


def delete_command(args: argparse.Namespace) -> None:
    folder = machine_folder(args.host)
    if folder.exists():
        shutil.rmtree(folder)
    else:
        raise ClanError(f"Machine {args.host} does not exist")


def register_delete_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("host", type=str)
    parser.set_defaults(func=delete_command)
