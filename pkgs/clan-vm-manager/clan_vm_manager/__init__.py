import argparse
import sys

import gi

from .app import Application

gi.require_version("Gtk", "3.0")


def join_command(args: argparse.Namespace) -> None:
    print("Joining the flake")
    print(args.clan_uri)


def register_join_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("clan_uri", type=str, help="machine in the flake to run")
    parser.set_defaults(func=join_command)


def start_app(args: argparse.Namespace) -> None:
    app = Application(args)
    return app.run(sys.argv)


def main() -> None:
    parser = argparse.ArgumentParser(description="clan-vm-manager")
    subparser = parser.add_subparsers(
        title="command",
        description="command to execute",
        help="the command to execute",
        required=True,
    )
    register_join_parser(subparser.add_parser("join", help="join a clan"))
    parser.set_defaults(func=start_app)
    args = parser.parse_args()
    args.func(args)
