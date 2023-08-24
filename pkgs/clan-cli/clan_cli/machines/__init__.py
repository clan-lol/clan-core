# !/usr/bin/env python3
import argparse

from .update import register_update_parser


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )

    groups_parser = subparser.add_parser("update", help="Update a machine")
    register_update_parser(groups_parser)
