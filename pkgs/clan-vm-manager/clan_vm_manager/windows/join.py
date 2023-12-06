from ..app import Application
import argparse
from .overview import OverviewWindow
from clan_cli.clan_uri import ClanURI


def show_join(args: argparse.Namespace) -> None:
    print(f"Joining clan {args.clan_uri}")
    app = Application(OverviewWindow)
    return app.run()


def register_join_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("clan_uri", type=ClanURI, help="clan URI to join")
    parser.set_defaults(func=show_join)

