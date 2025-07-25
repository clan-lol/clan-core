# !/usr/bin/env python3
import argparse
import logging
from pathlib import Path

from clan_lib.clan.create import CreateOptions, create_clan
from clan_lib.errors import ClanError

from clan_cli.completions import add_dynamic_completer, complete_templates_clan
from clan_cli.vars.keygen import create_secrets_user_auto

log = logging.getLogger(__name__)


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    template_action = parser.add_argument(
        "--template",
        type=str,
        help="""Reference to the template to use for the clan. default="default". In the format '<flake_ref>#template_name' Where <flake_ref> is a flake reference (e.g. github:org/repo) or a local path (e.g. '.' ).
        Omitting '<flake_ref>#' will use the builtin templates (e.g. just 'default' from clan-core ).
        """,
        default="default",
    )
    add_dynamic_completer(template_action, complete_templates_clan)

    parser.add_argument(
        "--no-git",
        help="Do not setup git",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "name",
        type=str,
        nargs="?",
        help="Name of the clan to create. If not provided, will prompt for a name.",
    )

    parser.add_argument(
        "--no-update",
        help="Do not update the clan flake",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--user",
        help="The user to generate the keys for. Default: logged-in OS username (e.g. from $LOGNAME or system)",
        default=None,
    )

    def create_flake_command(args: argparse.Namespace) -> None:
        # Ask for a path interactively if none provided
        if args.name is None:
            user_input = input("Enter a name for the new clan: ").strip()
            if not user_input:
                msg = "Error: name is required."
                raise ClanError(msg)

            args.name = Path(user_input)

        create_clan(
            CreateOptions(
                dest=Path(args.name),
                template=args.template,
                setup_git=not args.no_git,
                src_flake=args.flake,
                update_clan=not args.no_update,
            )
        )
        create_secrets_user_auto(
            flake_dir=Path(args.name).resolve(),
            user=args.user,
            force=True,
        )

    parser.set_defaults(func=create_flake_command)
