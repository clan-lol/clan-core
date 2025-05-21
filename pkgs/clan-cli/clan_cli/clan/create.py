# !/usr/bin/env python3
import argparse
import logging
from pathlib import Path

from clan_lib.clan.create import CreateOptions, create_clan
from clan_lib.templates import (
    InputPrio,
)

log = logging.getLogger(__name__)


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--input",
        type=str,
        help="""Flake input name to use as template source
        can be specified multiple times, inputs are tried in order of definition
        Example: --input clan --input clan-core
        """,
        action="append",
        default=[],
    )

    parser.add_argument(
        "--no-self",
        help="Do not look into own flake for templates",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--template",
        type=str,
        help="Clan template name",
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
        help="Path where to write the clan template to",
        default=Path(),
    )

    parser.add_argument(
        "--no-update",
        help="Do not update the clan flake",
        action="store_true",
        default=False,
    )

    def create_flake_command(args: argparse.Namespace) -> None:
        if len(args.input) == 0:
            args.input = ["clan", "clan-core"]

        if args.no_self:
            input_prio = InputPrio.try_inputs(tuple(args.input))
        else:
            input_prio = InputPrio.try_self_then_inputs(tuple(args.input))

        create_clan(
            CreateOptions(
                input_prio=input_prio,
                dest=args.path,
                template_name=args.template,
                setup_git=not args.no_git,
                src_flake=args.flake,
                update_clan=not args.no_update,
            )
        )

    parser.set_defaults(func=create_flake_command)
