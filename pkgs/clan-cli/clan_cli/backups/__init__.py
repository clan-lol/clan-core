# !/usr/bin/env python3
import argparse

from .create import register_create_parser
from .list import register_list_parser
from .restore import register_restore_parser


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )

    list_parser = subparser.add_parser("list", help="list backups")
    register_list_parser(list_parser)

    create_parser = subparser.add_parser("create", help="create backups")
    register_create_parser(create_parser)

    restore_parser = subparser.add_parser("restore", help="restore backups")
    register_restore_parser(restore_parser)
