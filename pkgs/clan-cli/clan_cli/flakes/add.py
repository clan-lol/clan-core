# !/usr/bin/env python3
import argparse
from pathlib import Path
from typing import Dict

from pydantic import AnyUrl
from pydantic.tools import parse_obj_as

from clan_cli.dirs import user_history_file

from ..async_cmd import CmdOut, runforcli

DEFAULT_URL: AnyUrl = parse_obj_as(
    AnyUrl,
    "git+https://git.clan.lol/clan/clan-core?new-clan",
)


async def add_flake(path: Path) -> Dict[str, CmdOut]:
    user_history_file().parent.mkdir(parents=True, exist_ok=True)
    # append line to history file
    # TODO: Is this atomic?
    with open(user_history_file(), "a+") as f:
        f.write(f"{path}\n")
    return {}


def add_flake_command(args: argparse.Namespace) -> None:
    runforcli(add_flake, args.path)


# takes a (sub)parser and configures it
def register_add_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", type=Path, help="Path to the flake", default=Path("."))
    parser.set_defaults(func=add_flake_command)
