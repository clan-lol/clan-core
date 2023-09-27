import argparse
import json
import os
import subprocess

from ..dirs import get_clan_flake_toplevel, module_root
from ..errors import ClanError
from ..nix import nix_build, nix_config, nix_eval


def upload_secrets(machine: str) -> None:
    clan_dir = get_clan_flake_toplevel().as_posix()
    config = nix_config()
    system = config["system"]

    proc = subprocess.run(
        nix_build(
            [f'{clan_dir}#clanInternals.machines."{system}"."{machine}".uploadSecrets']
        ),
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )

    env = os.environ.copy()
    env["PYTHONPATH"] = str(module_root().parent)  # TODO do this in the clanCore module
    host = json.loads(
        subprocess.run(
            nix_eval(
                [
                    f'{clan_dir}#clanInternals.machines."{system}"."{machine}".deploymentAddress'
                ]
            ),
            stdout=subprocess.PIPE,
            text=True,
            check=True,
        ).stdout
    )

    secret_upload_script = proc.stdout.strip()
    secret_upload = subprocess.run(
        [
            secret_upload_script,
            host,
        ],
        env=env,
    )

    if secret_upload.returncode != 0:
        raise ClanError("failed to upload secrets")
    else:
        print("successfully uploaded secrets")


def upload_command(args: argparse.Namespace) -> None:
    upload_secrets(args.machine)


def register_upload_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to upload secrets to",
    )
    parser.set_defaults(func=upload_command)
