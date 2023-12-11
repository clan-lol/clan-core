# !/usr/bin/env python3
import argparse

from .add import register_add_parser
from .list import register_list_parser
from .update import register_update_parser


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )
    add_parser = subparser.add_parser("add", help="Add a clan flake")
    register_add_parser(add_parser)
    list_parser = subparser.add_parser("list", help="List recently used flakes")
    register_list_parser(list_parser)
    update_parser = subparser.add_parser("update", help="Update a clan flake")
    register_update_parser(update_parser)
