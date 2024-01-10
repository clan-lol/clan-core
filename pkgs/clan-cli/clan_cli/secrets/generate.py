import argparse
import logging
import os
import sys

from ..cmd import run
from ..machines.machines import Machine

log = logging.getLogger(__name__)


def generate_secrets(machine: Machine) -> None:
    env = os.environ.copy()
    env["CLAN_DIR"] = str(machine.flake_dir)
    env["PYTHONPATH"] = ":".join(sys.path)  # TODO do this in the clanCore module

    print(f"generating secrets... {machine.generate_secrets}")
    run(
        [machine.generate_secrets],
        env=env,
        error_msg="failed to generate secrets",
    )

    print("successfully generated secrets")


def generate_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake_dir=args.flake)
    generate_secrets(machine)


def register_generate_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to generate secrets for",
    )
    parser.set_defaults(func=generate_command)
