# !/usr/bin/env python3
import argparse
import os
from dataclasses import dataclass
from pathlib import Path

from clan_cli.api import API
from clan_cli.inventory import Inventory, init_inventory

from ..cmd import CmdOut, run
from ..errors import ClanError
from ..nix import nix_command, nix_shell

default_template_url: str = "git+https://git.clan.lol/clan/clan-core"
minimal_template_url: str = "git+https://git.clan.lol/clan/clan-core#templates.minimal"


@dataclass
class CreateClanResponse:
    flake_init: CmdOut
    git_init: CmdOut | None
    git_add: CmdOut
    git_config_username: CmdOut | None
    git_config_email: CmdOut | None
    flake_update: CmdOut


@dataclass
class CreateOptions:
    directory: Path | str
    # URL to the template to use. Defaults to the "minimal" template
    template_url: str = minimal_template_url
    initial: Inventory | None = None


def git_command(directory: Path, *args: str) -> list[str]:
    return nix_shell(["nixpkgs#git"], ["git", "-C", str(directory), *args])


@API.register
def create_clan(options: CreateOptions) -> CreateClanResponse:
    directory = Path(options.directory).resolve()
    template_url = options.template_url
    if not directory.exists():
        directory.mkdir()
    else:
        # Directory already exists
        # Check if it is empty
        # Throw error otherwise
        dir_content = os.listdir(directory)
        if len(dir_content) != 0:
            raise ClanError(
                location=f"{directory.resolve()}",
                msg="Cannot create clan",
                description="Directory already exists and is not empty.",
            )

    command = nix_command(
        [
            "flake",
            "init",
            "-t",
            template_url,
        ]
    )
    flake_init = run(command, cwd=directory)

    git_init = None
    if not directory.joinpath(".git").exists():
        git_init = run(git_command(directory, "init"))
    git_add = run(git_command(directory, "add", "."))

    # check if username is set
    has_username = run(git_command(directory, "config", "user.name"), check=False)
    git_config_username = None
    if has_username.returncode != 0:
        git_config_username = run(
            git_command(directory, "config", "user.name", "clan-tool")
        )

    has_username = run(git_command(directory, "config", "user.email"), check=False)
    git_config_email = None
    if has_username.returncode != 0:
        git_config_email = run(
            git_command(directory, "config", "user.email", "clan@example.com")
        )

    flake_update = run(
        nix_shell(["nixpkgs#nix"], ["nix", "flake", "update"]), cwd=directory
    )

    if options.initial:
        init_inventory(options.directory, init=options.initial)

    response = CreateClanResponse(
        flake_init=flake_init,
        git_init=git_init,
        git_add=git_add,
        git_config_username=git_config_username,
        git_config_email=git_config_email,
        flake_update=flake_update,
    )
    return response


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--url",
        type=str,
        help="url to the clan template",
        default=default_template_url,
    )

    parser.add_argument(
        "path", type=Path, help="Path to the clan directory", default=Path(".")
    )

    def create_flake_command(args: argparse.Namespace) -> None:
        create_clan(
            CreateOptions(
                directory=args.path,
                template_url=args.url,
            )
        )

    parser.set_defaults(func=create_flake_command)
