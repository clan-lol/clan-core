# !/usr/bin/env python3
import argparse
import subprocess

from .nix import nix_command


def create(args: argparse.Namespace) -> None:
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
    parser.set_defaults(func=create)
