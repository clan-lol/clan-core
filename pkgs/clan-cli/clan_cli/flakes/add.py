# !/usr/bin/env python3
import argparse
from pathlib import Path

from clan_cli.dirs import user_history_file

from ..async_cmd import CmdOut, runforcli
from ..locked_open import locked_open


async def add_flake(path: Path) -> dict[str, CmdOut]:
    user_history_file().parent.mkdir(parents=True, exist_ok=True)
    # append line to history file
    lines: set = set()
    old_lines = set()
    with locked_open(user_history_file(), "w+") as f:
        old_lines = set(f.readlines())
        lines = old_lines | {str(path)}
        if old_lines != lines:
            f.seek(0)
            f.writelines(lines)
            f.truncate()
    return {}


def add_flake_command(args: argparse.Namespace) -> None:
    runforcli(add_flake, args.path)


# takes a (sub)parser and configures it
def register_add_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", type=Path, help="Path to the flake", default=Path("."))
    parser.set_defaults(func=add_flake_command)
