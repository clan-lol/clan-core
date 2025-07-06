# !/usr/bin/env python3
import argparse
from .list import register_list_parser


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )
    list_parser = subparser.add_parser("list", help="List avilable templates")
    register_list_parser(list_parser)
