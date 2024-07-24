import argparse
import logging
from pathlib import Path

from clan_cli.api import API
from clan_cli.inventory import Machine, load_inventory_eval

log = logging.getLogger(__name__)


@API.register
def list_machines(flake_url: str | Path, debug: bool = False) -> dict[str, Machine]:
    inventory = load_inventory_eval(flake_url)
    return inventory.machines


def list_command(args: argparse.Namespace) -> None:
    flake_path = args.flake.path
    for name in list_machines(flake_path, args.debug).keys():
        print(name)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_command)
