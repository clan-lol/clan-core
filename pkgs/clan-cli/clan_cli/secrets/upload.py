import argparse
import json
import subprocess

from clan_cli.errors import ClanError

from ..dirs import get_clan_flake_toplevel
from ..nix import nix_build, nix_eval


def upload_secrets(machine: str) -> None:
    clan_dir = get_clan_flake_toplevel().as_posix()

    proc = subprocess.run(
        nix_build(
            [
                f'{clan_dir}#nixosConfigurations."{machine}".config.system.clan.uploadSecrets'
            ]
        ),
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    host = json.loads(
        subprocess.run(
            nix_eval(
                [
                    f'{clan_dir}#nixosConfigurations."{machine}".config.clan.networking.deploymentAddress'
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
