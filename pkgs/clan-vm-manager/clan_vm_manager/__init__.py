import argparse


from .app import Application
from clan_cli.clan_uri import ClanURI

from .windows.join import register_join_parser
from .windows.overview import show_overview, OverviewWindow


def main() -> None:
    parser = argparse.ArgumentParser(description="clan-vm-manager")

    # Add join subcommand
    subparser = parser.add_subparsers(
        title="command",
        description="command to execute",
        help="the command to execute",
    )
    register_join_parser(subparser.add_parser("join", help="join a clan"))

    # Executed when no command is given
    parser.set_defaults(func=show_overview)
    args = parser.parse_args()
    args.func(args)
