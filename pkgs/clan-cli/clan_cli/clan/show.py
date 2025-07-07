import argparse
import logging

from clan_lib.clan.get import get_clan_details

log = logging.getLogger(__name__)


def show_command(args: argparse.Namespace) -> None:
    flake_path = args.flake.path
    meta = get_clan_details(flake_path)

    print(f"Name: {meta.get('name')}")
    print(f"Description: {meta.get('description', '-')}")
    print(f"Icon: {meta.get('icon', '-')}")


def register_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=show_command)
    parser.add_argument(
        "show",
        help="Show",
    )
