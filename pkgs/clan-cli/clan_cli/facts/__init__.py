# !/usr/bin/env python3
import argparse

from .check import register_check_parser
from .generate import register_generate_parser
from .list import register_list_parser
from .upload import register_upload_parser


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )

    check_parser = subparser.add_parser("check", help="check if facts are up to date")
    register_check_parser(check_parser)

    list_parser = subparser.add_parser("list", help="list all facts")
    register_list_parser(list_parser)

    parser_generate = subparser.add_parser(
        "generate", help="generate secrets for machines if they don't exist yet"
    )
    register_generate_parser(parser_generate)

    parser_upload = subparser.add_parser("upload", help="upload secrets for machines")
    register_upload_parser(parser_upload)
