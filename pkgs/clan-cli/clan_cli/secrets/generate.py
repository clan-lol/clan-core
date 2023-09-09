import argparse
import subprocess
import sys

from clan_cli.errors import ClanError

from ..dirs import get_clan_flake_toplevel


def generate_secrets(machine: str) -> None:
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
            "; }]; }).config.system.clan.generateSecrets",
        ],
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
