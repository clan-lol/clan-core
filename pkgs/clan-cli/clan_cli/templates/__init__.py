# !/usr/bin/env python3
import argparse

from .apply import register_apply_parser
from .info import register_info_parser
from .list import register_list_parser


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )
    list_parser = subparser.add_parser("list", help="List available templates")
    apply_parser = subparser.add_parser(
        "apply",
        help="Apply a template of the specified type",
    )
    info_parser = subparser.add_parser(
        "info",
        help="Show template placeholders and valid options",
    )
    register_list_parser(list_parser)
    register_apply_parser(apply_parser)
    register_info_parser(info_parser)
