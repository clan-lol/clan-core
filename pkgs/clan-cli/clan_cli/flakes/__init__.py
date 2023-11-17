# !/usr/bin/env python3
import argparse

from clan_cli.flakes.add import register_add_parser

from .create import register_create_parser


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
    add_parser = subparser.add_parser("add", help="Add a clan flake")
    register_add_parser(add_parser)
