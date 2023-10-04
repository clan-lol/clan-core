import argparse
import logging
import os
import subprocess
import sys

from clan_cli.errors import ClanError

from ..machines.machines import Machine

log = logging.getLogger(__name__)


def generate_secrets(machine: Machine) -> None:
    env = os.environ.copy()
    env["CLAN_DIR"] = str(machine.clan_dir)
    env["PYTHONPATH"] = ":".join(sys.path)  # TODO do this in the clanCore module

    print(f"generating secrets... {machine.generate_secrets}")
    proc = subprocess.run(
        [machine.generate_secrets],
        env=env,
    )

    if proc.returncode != 0:
        log.error("stdout: %s", proc.stdout)
        log.error("stderr: %s", proc.stderr)
        raise ClanError("failed to generate secrets")
    else:
        print("successfully generated secrets")


def generate_command(args: argparse.Namespace) -> None:
    machine = Machine(args.machine)
    generate_secrets(machine)


def register_generate_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to generate secrets for",
    )
    parser.set_defaults(func=generate_command)
