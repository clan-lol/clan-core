import argparse
import logging

from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_lib.flake import require_flake
from clan_lib.vars.check import check_vars

log = logging.getLogger(__name__)


def check_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    ok = check_vars(args.machine, flake, generator_name=args.generator)
    if not ok:
        raise SystemExit(1)


def register_check_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machine",
        help="The machine to check secrets for",
    )
    add_dynamic_completer(machines_parser, complete_machines)

    parser.add_argument(
        "--generator",
        "-g",
        help="the generator to check",
    )
    parser.set_defaults(func=check_command)
