# !/usr/bin/env python3
import argparse

from .deploy import register_deploy_parser
from .generate import register_generate_parser
from .groups import register_groups_parser
from .import_sops import register_import_sops_parser
from .key import register_key_parser
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

    import_sops_parser = subparser.add_parser("import-sops", help="import a sops file")
    register_import_sops_parser(import_sops_parser)

    parser_generate = subparser.add_parser(
        "generate", help="generate secrets for machines if they don't exist yet"
    )
    register_generate_parser(parser_generate)

    parser_deploy = subparser.add_parser("deploy", help="deploy secrets for machines")
    register_deploy_parser(parser_deploy)

    parser_key = subparser.add_parser("key", help="create and show age keys")
    register_key_parser(parser_key)

    register_secrets_parser(subparser)
