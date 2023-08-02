# !/usr/bin/env python3
import argparse

from .groups import register_groups_parser
from .machines import register_machines_parser
from .secrets import register_secrets_parser
from .users import register_users_parser


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )

    groups_parser = subparser.add_parser("groups", help="manage groups")
    register_groups_parser(groups_parser)

    users_parser = subparser.add_parser("users", help="manage users")
    register_users_parser(users_parser)

    machines_parser = subparser.add_parser("machines", help="manage machines")
    register_machines_parser(machines_parser)

    register_secrets_parser(subparser)
