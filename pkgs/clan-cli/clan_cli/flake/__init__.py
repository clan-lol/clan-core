# !/usr/bin/env python3
import argparse

from .create import register_create_parser


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )
    update_parser = subparser.add_parser("create", help="Create a clan flake")
    register_create_parser(update_parser)
