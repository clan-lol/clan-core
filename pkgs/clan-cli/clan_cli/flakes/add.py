# !/usr/bin/env python3
import argparse
from pathlib import Path

from clan_cli.dirs import user_history_file

from ..async_cmd import CmdOut, runforcli


async def add_flake(path: Path) -> dict[str, CmdOut]:
    user_history_file().parent.mkdir(parents=True, exist_ok=True)
    # append line to history file
    # TODO: Make this atomic
    lines: set[str] = set()
    if user_history_file().exists():
        with open(user_history_file()) as f:
            lines = set(f.readlines())
    lines.add(str(path))
    with open(user_history_file(), "w") as f:
        f.writelines(lines)
    return {}


def add_flake_command(args: argparse.Namespace) -> None:
    runforcli(add_flake, args.path)


# takes a (sub)parser and configures it
def register_add_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", type=Path, help="Path to the flake", default=Path("."))
    parser.set_defaults(func=add_flake_command)
