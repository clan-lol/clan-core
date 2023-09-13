import argparse
import subprocess
import sys

from clan_cli.errors import ClanError

from ..nix import nix_build_machine


def deploy_secrets(machine: str) -> None:
    proc = subprocess.run(
        nix_build_machine(
            machine=machine,
            attr=[
                "config",
                "system",
                "clan",
                "deploySecrets",
            ],
        ),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise ClanError(f"failed to deploy secrets:\n{proc.stderr}")

    secret_deploy_script = proc.stdout.strip()
    secret_deploy = subprocess.run(
        [
            secret_deploy_script,
            f"root@{machine}",
        ],
    )

    if secret_deploy.returncode != 0:
        raise ClanError("failed to deploy secrets")
    else:
        print("successfully deployed secrets")


def deploy_command(args: argparse.Namespace) -> None:
    deploy_secrets(args.machine)


def register_deploy_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to deploy secrets to",
    )
    parser.set_defaults(func=deploy_command)
