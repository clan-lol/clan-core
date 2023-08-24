# !/usr/bin/env python3
import argparse

from .create import register_create_parser
from .delete import register_delete_parser
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

    update_parser = subparser.add_parser("update", help="Update a machine")
    register_update_parser(update_parser)

    create_parser = subparser.add_parser("create", help="Create a machine")
    register_create_parser(create_parser)

    delete_parser = subparser.add_parser("delete", help="Delete a machine")
    register_delete_parser(delete_parser)

    list_parser = subparser.add_parser("list", help="List machines")
    register_list_parser(list_parser)
