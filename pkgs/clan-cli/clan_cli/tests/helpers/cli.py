import argparse
import logging
import shlex

from clan_cli.cli import create_flake_from_args, create_parser
from clan_lib.custom_logger import print_trace

log = logging.getLogger(__name__)


def run(args: list[str]) -> argparse.Namespace:
    parser = create_parser(prog="clan")
    parsed = parser.parse_args(args)
    cmd = shlex.join(["clan", *args])

    # Convert flake path to Flake object with nix_options if flake argument exists
    if hasattr(parsed, "flake") and parsed.flake is not None:
        parsed.flake = create_flake_from_args(parsed)

    print_trace(f"$ {cmd}", log, "localhost")
    if hasattr(parsed, "func"):
        parsed.func(parsed)
    return parsed
