import argparse
import os
import shlex
import subprocess
from pathlib import Path

from ..dirs import get_clan_flake_toplevel, module_root
from ..errors import ClanError
from ..nix import nix_build, nix_config


def build_upload_script(machine: str, clan_dir: Path) -> str:
    config = nix_config()
    system = config["system"]

    cmd = nix_build(
        [f'{clan_dir}#clanInternals.machines."{system}"."{machine}".uploadSecrets']
    )
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    if proc.returncode != 0:
        raise ClanError(
            f"failed to upload secrets:\n{shlex.join(cmd)}\nexited with {proc.returncode}"
        )

    return proc.stdout.strip()


def run_upload_secrets(flake_attr: str, clan_dir: Path) -> None:
    env = os.environ.copy()
    env["CLAN_DIR"] = str(clan_dir)
    env["PYTHONPATH"] = str(module_root().parent)  # TODO do this in the clanCore module
    print(f"uploading secrets... {flake_attr}")
    proc = subprocess.run(
        [flake_attr],
        env=env,
    )

    if proc.returncode != 0:
        raise ClanError("failed to upload secrets")
    else:
        print("successfully uploaded secrets")


def upload_secrets(machine: str) -> None:
    clan_dir = get_clan_flake_toplevel()
    run_upload_secrets(build_upload_script(machine, clan_dir), clan_dir)


def upload_command(args: argparse.Namespace) -> None:
    upload_secrets(args.machine)


def register_upload_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to upload secrets to",
    )
    parser.set_defaults(func=upload_command)
