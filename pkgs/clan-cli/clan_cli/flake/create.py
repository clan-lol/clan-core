# !/usr/bin/env python3
import argparse
import asyncio
from pathlib import Path
from typing import Tuple

from ..async_cmd import run
from ..errors import ClanError
from ..nix import nix_command

DEFAULT_URL = "git+https://git.clan.lol/clan/clan-core#new-clan"


async def create_flake(directory: Path, url: str) -> Tuple[bytes, bytes]:
    if not directory.exists():
        directory.mkdir()
    flake_command = nix_command(
        [
            "flake",
            "init",
            "-t",
            url,
        ]
    )
    stdout, stderr = await run(flake_command, directory)
    return stdout, stderr


def create_flake_command(args: argparse.Namespace) -> None:
    try:
        stdout, stderr = asyncio.run(create_flake(args.directory, DEFAULT_URL))
        print(stderr.decode("utf-8"), end="")
        print(stdout.decode("utf-8"), end="")
    except ClanError as e:
        print(e)
        exit(1)


# takes a (sub)parser and configures it
def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "directory",
        type=Path,
        help="output directory for the flake",
    )
    # parser.add_argument("name", type=str, help="name of the flake")
    parser.set_defaults(func=create_flake_command)
