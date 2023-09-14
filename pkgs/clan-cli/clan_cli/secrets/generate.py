import argparse
import os
import subprocess
import sys

from clan_cli.errors import ClanError

from ..dirs import get_clan_flake_toplevel
from ..nix import nix_build


def generate_secrets(machine: str) -> None:
    clan_dir = get_clan_flake_toplevel().as_posix().strip()
    env = os.environ.copy()
    env["CLAN_DIR"] = clan_dir

    proc = subprocess.run(
        nix_build(
            [
                f'path:{clan_dir}#nixosConfigurations."{machine}".config.system.clan.generateSecrets'
            ]
        ),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise ClanError(f"failed to generate secrets:\n{proc.stderr}")

    secret_generator_script = proc.stdout.strip()
    print(secret_generator_script)
    secret_generator = subprocess.run(
        [secret_generator_script],
        env=env,
    )

    if secret_generator.returncode != 0:
        raise ClanError("failed to generate secrets")
    else:
        print("successfully generated secrets")


def generate_command(args: argparse.Namespace) -> None:
    generate_secrets(args.machine)


def register_generate_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to generate secrets for",
    )
    parser.set_defaults(func=generate_command)
