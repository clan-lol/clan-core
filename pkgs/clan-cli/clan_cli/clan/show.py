import argparse
import logging

from clan_lib.clan.get import get_clan_details
from clan_lib.flake import require_flake

log = logging.getLogger(__name__)


def show_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    meta = get_clan_details(flake)

    print(f"Name: {meta.get('name')}")
    print(f"Description: {meta.get('description', '-')}")


def register_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=show_command)
    parser.add_argument(
        "show",
        help="Show",
    )
