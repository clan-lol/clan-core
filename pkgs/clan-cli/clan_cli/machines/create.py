import argparse
import logging

from clan_cli.config.machine import set_config_for_machine

log = logging.getLogger(__name__)


def create_command(args: argparse.Namespace) -> None:
    set_config_for_machine(args.flake, args.machine, dict())


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str)
    parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to create machine for",
    )
    parser.set_defaults(func=create_command)
