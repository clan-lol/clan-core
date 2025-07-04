import argparse
import logging

from clan_lib.flake import Flake
from clan_lib.machines.actions import list_machines

from clan_cli.completions import add_dynamic_completer, complete_tags

log = logging.getLogger(__name__)


def list_command(args: argparse.Namespace) -> None:
    flake: Flake = args.flake

    for name in list_machines(flake, opts={"filter": {"tags": args.tags}}):
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
