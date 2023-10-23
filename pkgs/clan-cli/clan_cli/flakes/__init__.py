# !/usr/bin/env python3
import argparse

from .create import register_create_parser
from .list import register_list_parser

# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )
    create_parser = subparser.add_parser("create", help="Create a clan flake")
    register_create_parser(create_parser)

    list_parser = subparser.add_parser("list", help="List clan flakes")
    register_list_parser(list_parser)
