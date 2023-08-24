import argparse
import os

from .folders import machines_folder
from .types import validate_hostname


def list_machines() -> list[str]:
    path = machines_folder()
    if not path.exists():
        return []
    objs: list[str] = []
    for f in os.listdir(path):
        if validate_hostname(f):
            objs.append(f)
    return objs


def list_command(args: argparse.Namespace) -> None:
    for machine in list_machines():
        print(machine)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_command)
