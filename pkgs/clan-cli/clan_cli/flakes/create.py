# !/usr/bin/env python3
import argparse
from pathlib import Path

from ..async_cmd import CmdOut, run, runforcli
from ..errors import ClanError
from ..nix import nix_command, nix_shell

DEFAULT_URL: str = "git+https://git.clan.lol/clan/clan-core?new-clan"


async def create_flake(directory: Path, url: str) -> dict[str, CmdOut]:
    if not directory.exists():
        directory.mkdir()
    else:
        raise ClanError(f"Flake at '{directory}' already exists")
    response = {}
    command = nix_command(
        [
            "flake",
            "init",
            "-t",
            url,
        ]
    )
    out = await run(command, cwd=directory)
    response["flake init"] = out

    command = nix_shell(["git"], ["git", "init"])
    out = await run(command, cwd=directory)
    response["git init"] = out

    command = nix_shell(["git"], ["git", "add", "."])
    out = await run(command, cwd=directory)
    response["git add"] = out

    # command = nix_shell(["git"], ["git", "config", "init.defaultBranch", "main"])
    # out = await run(command, cwd=directory)
    # response["git config"] = out

    command = nix_shell(["git"], ["git", "config", "user.name", "clan-tool"])
    out = await run(command, cwd=directory)
    response["git config"] = out

    command = nix_shell(["git"], ["git", "config", "user.email", "clan@example.com"])
    out = await run(command, cwd=directory)
    response["git config"] = out

    # TODO: Find out why this fails on Johannes machine
    # command = nix_shell(["git"], ["git", "commit", "-a", "-m", "Initial commit"])
    # out = await run(command, cwd=directory)
    # response["git commit"] = out

    return response


def create_flake_command(args: argparse.Namespace) -> None:
    runforcli(create_flake, args.path, args.url)


# takes a (sub)parser and configures it
def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--url",
        type=str,
        help="url for the flake",
        default=DEFAULT_URL,
    )
    parser.add_argument("path", type=Path, help="Path to the flake", default=Path("."))
    parser.set_defaults(func=create_flake_command)
