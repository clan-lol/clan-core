import argparse

from .inspect import register_inspect_parser
from .run import register_run_parser


def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="command to execute",
        help="the command to execute",
        required=True,
    )

    register_inspect_parser(
        subparser.add_parser("inspect", help="inspect the vm configuration"),
    )
    register_run_parser(subparser.add_parser("run", help="run a VM from a machine"))
