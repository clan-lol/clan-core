import argparse
import logging

from clan_lib.flake import Flake
from clan_lib.machines.list import list_full_machines, query_machines_by_tags

from clan_cli.completions import add_dynamic_completer, complete_tags

log = logging.getLogger(__name__)


def list_command(args: argparse.Namespace) -> None:
    flake: Flake = args.flake

    if args.tags:
        for name in query_machines_by_tags(flake, args.tags):
            print(name)
    else:
        for name in list_full_machines(flake):
            print(name)


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    tag_parser = parser.add_argument(
        "--tags",
        nargs="+",
        default=[],
        help="Tags that machines should be queried for. Multiple tags will intersect.",
    )
    add_dynamic_completer(tag_parser, complete_tags)
    parser.set_defaults(func=list_command)
