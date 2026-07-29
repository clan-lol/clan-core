import argparse
from pathlib import Path

from clan_lib.flake import require_flake
from clan_lib.vars.import_vars import import_vars


def _import_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    import_vars(flake, Path(args.folder))


def register_import_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "folder",
        help="The input folder to import from",
    )
    parser.set_defaults(func=_import_command)
