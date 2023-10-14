import argparse
import logging
import os

from ..dirs import clan_flakes_dir

log = logging.getLogger(__name__)


def list_flakes() -> list[str]:
    path = clan_flakes_dir()
    log.debug(f"Listing machines in {path}")
    if not path.exists():
        return []
    objs: list[str] = []
    for f in os.listdir(path):
        objs.append(f)
    return objs


def list_command(args: argparse.Namespace) -> None:
    for flake in list_flakes():
        print(flake)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_command)
