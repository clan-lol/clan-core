import argparse
import subprocess
import sys

from clan_cli.errors import ClanError


def get_secret_script(machine: str) -> None:
    proc = subprocess.run(
        [
            "nix",
            "build",
            "--impure",
            "--print-out-paths",
            "--expr",
            "let f = builtins.getFlake (toString ./.); in "
            f"(f.nixosConfigurations.{machine}.extendModules "
            "{ modules = [{ clan.core.clanDir = toString ./.; }]; })"
            ".config.system.clan.generateSecrets",
        ],
        check=True,
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
        check=True,
    )

    if secret_generator.returncode != 0:
        raise ClanError("failed to generate secrets")
    else:
        print("successfully generated secrets")


def generate_command(args: argparse.Namespace) -> None:
    get_secret_script(args.machine)


def register_generate_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to generate secrets for",
    )
    parser.set_defaults(func=generate_command)
