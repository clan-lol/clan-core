# !/usr/bin/env python3
import argparse
import sys

import argcomplete

import clan_admin


# this will be the entrypoint under /bin/clan (see pyproject.toml config)
def clan() -> None:
    parser = argparse.ArgumentParser(description="cLAN tool")
    subparsers = parser.add_subparsers()

    # init clan admin
    parser_admin = subparsers.add_parser("admin")
    clan_admin.make_parser(parser_admin)
    argcomplete.autocomplete(parser)
    parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
