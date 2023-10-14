import argparse
import logging
import os

from ..dirs import machines_dir
from ..flakes.types import FlakeName
from .types import validate_hostname

log = logging.getLogger(__name__)


def list_machines(flake_name: FlakeName) -> list[str]:
    path = machines_dir(flake_name)
    log.debug(f"Listing machines in {path}")
    if not path.exists():
        return []
    objs: list[str] = []
    for f in os.listdir(path):
        if validate_hostname(f):
            objs.append(f)
    return objs


def list_command(args: argparse.Namespace) -> None:
    for machine in list_machines(args.flake):
        print(machine)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to create machine for",
    )
    parser.set_defaults(func=list_command)
