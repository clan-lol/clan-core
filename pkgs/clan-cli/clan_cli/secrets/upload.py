import argparse
import json
import subprocess
import sys
from pathlib import Path

from ..dirs import get_clan_flake_toplevel
from ..errors import ClanError
from ..nix import nix_build, nix_config, nix_eval
from ..ssh import parse_deployment_address
from .secrets import decrypt_secret, has_secret


def upload_secrets(machine: str) -> None:
    clan_dir = get_clan_flake_toplevel().as_posix()
    config = nix_config()
    system = config["system"]

    proc = subprocess.run(
        nix_build(
            [
                f'{clan_dir}#nixosConfigurations."{machine}".config.system.clan.{system}.uploadSecrets'
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


# this is called by the sops.nix clan core module
def upload_age_key_from_nix(
    machine_name: str, deployment_address: str, age_key_file: str
) -> None:
    secret_name = f"{machine_name}-age.key"
    if not has_secret(secret_name):  # skip uploading the secret, not managed by us
        return
    secret = decrypt_secret(secret_name)

    h = parse_deployment_address(machine_name, deployment_address)
    path = Path(age_key_file)

    proc = h.run(
        [
            "bash",
            "-c",
            'mkdir -p "$0" && echo -n "$1" > "$2"',
            str(path.parent),
            secret,
            age_key_file,
        ],
        check=False,
    )
    if proc.returncode != 0:
        print(f"failed to upload age key to {deployment_address}")
        sys.exit(1)


def upload_command(args: argparse.Namespace) -> None:
    upload_secrets(args.machine)


def register_upload_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to upload secrets to",
    )
    parser.set_defaults(func=upload_command)
