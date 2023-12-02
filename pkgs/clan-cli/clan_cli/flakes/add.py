# !/usr/bin/env python3
import argparse
from pathlib import Path

from clan_cli.flakes.history import push_history

from ..async_cmd import CmdOut, runforcli


async def add_flake(path: Path) -> dict[str, CmdOut]:
    push_history(path)
    return {}


def add_flake_command(args: argparse.Namespace) -> None:
    runforcli(add_flake, args.path)


# takes a (sub)parser and configures it
def register_add_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", type=Path, help="Path to the flake", default=Path("."))
    parser.set_defaults(func=add_flake_command)
