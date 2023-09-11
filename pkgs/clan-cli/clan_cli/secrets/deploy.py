import argparse
import subprocess
import sys

from clan_cli.errors import ClanError

from ..dirs import get_clan_flake_toplevel


def deploy_secrets(machine: str) -> None:
    clan_flake = get_clan_flake_toplevel()
    proc = subprocess.run(
        [
            "nix",
            "build",
            "--impure",
            "--print-out-paths",
            "--expr",
            f'let f = builtins.getFlake "{clan_flake}"; in '
            "(f.nixosConfigurations."
            f"{machine}"
            ".extendModules { modules = [{ clanCore.clanDir = "
            f"{clan_flake}"
            "; }]; }).config.system.clan.deploySecrets",
        ],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr, file=sys.stderr)
        raise ClanError(f"failed to deploy secrets:\n{proc.stderr}")

    secret_deploy_script = proc.stdout.strip()
    secret_deploy = subprocess.run(
        [secret_deploy_script],
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
