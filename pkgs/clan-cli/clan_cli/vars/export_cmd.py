import argparse
from pathlib import Path

from clan_lib.flake import require_flake
from clan_lib.vars.export_vars import export_vars


def _export_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    export_vars(flake, Path(args.folder))


def register_export_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "folder",
        help="The output folder for the export (must not exist)",
    )
    parser.set_defaults(func=_export_command)
