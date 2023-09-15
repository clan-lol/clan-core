# !/usr/bin/env python3
import argparse
import os
import subprocess

from .nix import nix_command


def create(args: argparse.Namespace) -> None:
    os.makedirs(args.folder, exist_ok=True)
    # TODO create clan template in flake
    subprocess.run(
        nix_command(
            [
                "flake",
                "init",
                "-t",
                "git+https://git.clan.lol/clan/clan-core#new-clan",
            ]
        ),
        check=True,
    )


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-f",
        "--folder",
        help="the folder where the clan is defined, default to the current folder",
        default=os.getcwd(),
    )
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )

    parser_create = subparser.add_parser("create", help="create a new clan")
    parser_create.set_defaults(func=create)
