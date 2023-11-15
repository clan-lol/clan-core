import argparse
import logging
import os
from pathlib import Path

from ..dirs import machines_dir
from .types import validate_hostname

log = logging.getLogger(__name__)


def list_machines(flake_dir: Path) -> list[str]:
    path = machines_dir(flake_dir)
    log.debug(f"Listing machines in {path}")
    if not path.exists():
        return []
    objs: list[str] = []
    for f in os.listdir(path):
        if validate_hostname(f):
            objs.append(f)
    return objs


def list_command(args: argparse.Namespace) -> None:
    for machine in list_machines(Path(args.flake)):
        print(machine)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_command)
