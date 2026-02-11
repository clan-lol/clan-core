import argparse

from .run import register_run_parser


def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="command to execute",
        help="the command to execute",
        required=True,
    )

    register_run_parser(subparser.add_parser("run", help="run a VM from a machine"))
