import argparse
import os
import shlex
import subprocess
from pathlib import Path

from clan_cli.errors import ClanError

from ..dirs import get_clan_flake_toplevel, module_root
from ..nix import nix_build, nix_config


def build_generate_script(machine: str, clan_dir: Path) -> str:
    config = nix_config()
    system = config["system"]

    cmd = nix_build(
        [
            f'path:{clan_dir}#clanInternals.machines."{system}"."{machine}".generateSecrets'
        ]
    )
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise ClanError(
            f"failed to generate secrets:\n{shlex.join(cmd)}\nexited with {proc.returncode}"
        )

    return proc.stdout.strip()


def run_generate_secrets(secret_generator_script: str, clan_dir: Path) -> None:
    env = os.environ.copy()
    env["CLAN_DIR"] = str(clan_dir)
    env["PYTHONPATH"] = str(module_root().parent)  # TODO do this in the clanCore module
    print(f"generating secrets... {secret_generator_script}")
    proc = subprocess.run(
        [secret_generator_script],
        env=env,
    )

    if proc.returncode != 0:
        raise ClanError("failed to generate secrets")
    else:
        print("successfully generated secrets")


def generate(machine: str) -> None:
    clan_dir = get_clan_flake_toplevel()
    run_generate_secrets(build_generate_script(machine, clan_dir), clan_dir)


def generate_command(args: argparse.Namespace) -> None:
    generate(args.machine)


def register_generate_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to generate secrets for",
    )
    parser.set_defaults(func=generate_command)
