import argparse
import subprocess
import sys

from clan_cli.errors import ClanError

from ..nix import nix_build_machine


def upload_secrets(machine: str) -> None:
    proc = subprocess.run(
        nix_build_machine(
            machine=machine,
            attr=[
                "config",
                "system",
                "clan",
                "uploadSecrets",
            ],
        ),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise ClanError(f"failed to upload secrets:\n{proc.stderr}")

    secret_upload_script = proc.stdout.strip()
    secret_upload = subprocess.run(
        [
            secret_upload_script,
            f"root@{machine}",
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
