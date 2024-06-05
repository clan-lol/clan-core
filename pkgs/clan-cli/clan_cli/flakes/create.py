# !/usr/bin/env python3
import argparse
from dataclasses import dataclass
from pathlib import Path

from clan_cli.api import API

from ..cmd import CmdOut, run
from ..errors import ClanError
from ..nix import nix_command, nix_shell

DEFAULT_TEMPLATE_URL: str = "git+https://git.clan.lol/clan/clan-core"


@dataclass
class CreateClanResponse:
    git_init: CmdOut
    git_add: CmdOut
    git_config: CmdOut
    flake_update: CmdOut


@API.register
def create_clan(directory: Path, template_url: str) -> CreateClanResponse:
    if not directory.exists():
        directory.mkdir()
    else:
        raise ClanError(
            location=f"{directory.resolve()}",
            msg="Cannot create clan",
            description="Directory already exists",
        )

    cmd_responses = {}
    command = nix_command(
        [
            "flake",
            "init",
            "-t",
            template_url,
        ]
    )
    out = run(command, cwd=directory)

    command = nix_shell(["nixpkgs#git"], ["git", "init"])
    out = run(command, cwd=directory)
    cmd_responses["git init"] = out

    command = nix_shell(["nixpkgs#git"], ["git", "add", "."])
    out = run(command, cwd=directory)
    cmd_responses["git add"] = out

    command = nix_shell(["nixpkgs#git"], ["git", "config", "user.name", "clan-tool"])
    out = run(command, cwd=directory)
    cmd_responses["git config"] = out

    command = nix_shell(
        ["nixpkgs#git"], ["git", "config", "user.email", "clan@example.com"]
    )
    out = run(command, cwd=directory)
    cmd_responses["git config"] = out

    command = ["nix", "flake", "update"]
    out = run(command, cwd=directory)
    cmd_responses["flake update"] = out

    response = CreateClanResponse(
        git_init=cmd_responses["git init"],
        git_add=cmd_responses["git add"],
        git_config=cmd_responses["git config"],
        flake_update=cmd_responses["flake update"],
    )
    return response


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--url",
        type=str,
        help="url to the clan template",
        default=DEFAULT_TEMPLATE_URL,
    )
    parser.add_argument(
        "path", type=Path, help="Path to the clan directory", default=Path(".")
    )

    def create_flake_command(args: argparse.Namespace) -> None:
        create_clan(args.path, args.url)

    parser.set_defaults(func=create_flake_command)
