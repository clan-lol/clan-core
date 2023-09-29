import argparse

from .create import register_create_parser
from .inspect import register_inspect_parser


def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="command to execute",
        help="the command to execute",
        required=True,
    )

    inspect_parser = subparser.add_parser(
        "inspect", help="inspect the vm configuration"
    )
    register_inspect_parser(inspect_parser)

    create_parser = subparser.add_parser("create", help="create a VM from a machine")
    register_create_parser(create_parser)
