import argparse

from .app import (
    register_join_parser,
    register_overview_parser,
    register_run_parser,
    show_overview,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="clan-vm-manager")

    # Add join subcommand
    subparser = parser.add_subparsers(
        title="command",
        description="command to execute",
        help="the command to execute",
    )
    register_join_parser(subparser.add_parser("join", help="join a clan"))

    register_overview_parser(subparser.add_parser("overview", help="overview screen"))

    register_run_parser(subparser.add_parser("run", help="run a vm"))

    # Executed when no command is given
    parser.set_defaults(func=show_overview)
    args = parser.parse_args()
    args.func(args)
