import argparse
import logging
import os
import subprocess
import sys

from clan_cli.errors import ClanError

from ..dirs import specific_flake_dir
from ..machines.machines import Machine
from ..types import FlakeName

log = logging.getLogger(__name__)


def generate_secrets(machine: Machine, flake_name: FlakeName) -> None:
    env = os.environ.copy()
    env["CLAN_DIR"] = str(machine.flake_dir)
    env["PYTHONPATH"] = ":".join(sys.path)  # TODO do this in the clanCore module

    print(f"generating secrets... {machine.generate_secrets}")
    proc = subprocess.run(
        [machine.generate_secrets, flake_name],
        env=env,
    )

    if proc.returncode != 0:
        raise ClanError("failed to generate secrets")
    else:
        print("successfully generated secrets")


def generate_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake_dir=specific_flake_dir(args.flake))
    generate_secrets(machine, args.flake)


def register_generate_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to generate secrets for",
    )
    parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to create machine for",
    )
    parser.set_defaults(func=generate_command)
