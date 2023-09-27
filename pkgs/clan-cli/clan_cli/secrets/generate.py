import argparse
import os
import shlex
import subprocess

from clan_cli.errors import ClanError

from ..dirs import get_clan_flake_toplevel, module_root
from ..nix import nix_build, nix_config


def generate_secrets(machine: str) -> None:
    clan_dir = get_clan_flake_toplevel().as_posix().strip()
    env = os.environ.copy()
    env["CLAN_DIR"] = clan_dir
    env["PYTHONPATH"] = str(module_root().parent)  # TODO do this in the clanCore module
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
