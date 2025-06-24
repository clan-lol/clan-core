import argparse
import logging

from clan_lib.dirs import get_clan_flake_toplevel_or_env
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.morph import morph_machine

log = logging.getLogger(__name__)


def morph_command(args: argparse.Namespace) -> None:
    if args.flake:
        clan_dir = args.flake
    else:
        tmp = get_clan_flake_toplevel_or_env()
        clan_dir = Flake(str(tmp)) if tmp else None

    if not clan_dir:
        msg = "No clan found."
        description = (
            "Run this command in a clan directory or specify the --flake option"
        )
        raise ClanError(msg, description=description)

    morph_machine(
        flake=Flake(str(args.flake)),
        template=args.template,
        ask_confirmation=args.confirm_firing,
        name=args.name,
    )


def register_morph_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=morph_command)

    parser.add_argument(
        "template",
        default="new-machine",
        type=str,
        help="The name of the template to use",
        nargs="?",
    )

    parser.add_argument(
        "--name",
        type=str,
        help="The name of the machine",
    )

    parser.add_argument(
        "--i-will-be-fired-for-using-this",
        dest="confirm_firing",
        default=True,
        action="store_false",
        help="Don't use unless you know what you are doing!",
    )
