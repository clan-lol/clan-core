# !/usr/bin/env python3
import argparse
import logging
from pathlib import Path

from clan_lib.clan.create import CreateOptions, create_clan
from clan_lib.errors import ClanError

log = logging.getLogger(__name__)


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--template",
        type=str,
        help="""Reference to the template to use for the clan. default="default". In the format '<flake_ref>#template_name' Where <flake_ref> is a flake reference (e.g. github:org/repo) or a local path (e.g. '.' ).
        Omitting '<flake_ref>#' will use the builtin templates (e.g. just 'default' from clan-core ).
        """,
        default="default",
    )

    parser.add_argument(
        "--no-git",
        help="Do not setup git",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "path",
        type=Path,
        nargs="?",
        help="Path where to write the clan template to",
    )

    parser.add_argument(
        "--no-update",
        help="Do not update the clan flake",
        action="store_true",
        default=False,
    )

    def create_flake_command(args: argparse.Namespace) -> None:
        # Ask for a path interactively if none provided
        if args.path is None:
            user_input = input("Enter a name for the new clan: ").strip()
            if not user_input:
                msg = "Error: name is required."
                raise ClanError(msg)

            args.path = Path(user_input)

        create_clan(
            CreateOptions(
                dest=args.path,
                template=args.template,
                setup_git=not args.no_git,
                src_flake=args.flake,
                update_clan=not args.no_update,
            )
        )

    parser.set_defaults(func=create_flake_command)
