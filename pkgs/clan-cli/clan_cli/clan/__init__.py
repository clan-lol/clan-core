# !/usr/bin/env python3
import argparse

from clan_cli.clan.inspect import register_inspect_parser

from .create import register_create_parser


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )
    create_parser = subparser.add_parser("create", help="Create a clan")
    register_create_parser(create_parser)
    inspect_parser = subparser.add_parser(
        "inspect",
        help="Inspect a clan",
        description="""Inspects the flake and prints some medata.
Deprecated - This command is marked for removal in the next release""",
    )
    register_inspect_parser(inspect_parser)
