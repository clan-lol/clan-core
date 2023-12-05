import argparse

from .app import Application


def join_command(args: argparse.Namespace) -> None:
    print("Joining the flake")
    print(args.clan_uri)
    app = Application()
    return app.run()


def register_join_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("clan_uri", type=str, help="clan URI to join")
    parser.set_defaults(func=join_command)


def start_app(args: argparse.Namespace) -> None:
    app = Application()
    return app.run()


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
    parser.set_defaults(func=start_app)
    args = parser.parse_args()
    args.func(args)
