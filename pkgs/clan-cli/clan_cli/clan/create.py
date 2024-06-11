# !/usr/bin/env python3
import argparse
import json
import os
from dataclasses import dataclass, fields
from pathlib import Path

from clan_cli.api import API
from clan_cli.arg_actions import AppendOptionAction

from ..cmd import CmdOut, run
from ..errors import ClanError
from ..nix import nix_command, nix_shell

default_template_url: str = "git+https://git.clan.lol/clan/clan-core"
minimal_template_url: str = "git+https://git.clan.lol/clan/clan-core#templates.minimal"


@dataclass
class CreateClanResponse:
    git_init: CmdOut
    git_add: CmdOut
    git_config: CmdOut
    flake_update: CmdOut


@dataclass
class ClanMetaInfo:
    name: str
    description: str | None
    icon: str | None


@dataclass
class CreateOptions:
    directory: Path | str
    # Metadata for the clan
    # Metadata can be shown with `clan show`
    meta: ClanMetaInfo | None = None
    # URL to the template to use. Defaults to the "minimal" template
    template_url: str = minimal_template_url


@API.register
def create_clan(options: CreateOptions) -> CreateClanResponse:
    directory = Path(options.directory)
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

    # Write meta.json file if meta is provided
    if options.meta is not None:
        meta_file = Path(directory / "clan/meta.json")
        meta_file.parent.mkdir(parents=True, exist_ok=True)
        with open(meta_file, "w") as f:
            json.dump(options.meta.__dict__, f)

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
        default=default_template_url,
    )

    parser.add_argument(
        "--meta",
        help=f"""Metadata to set for the clan. Available options are: {", ".join([f.name for f in fields(ClanMetaInfo)]) }""",
        nargs=2,
        metavar=("name", "value"),
        action=AppendOptionAction,
        default=[],
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
