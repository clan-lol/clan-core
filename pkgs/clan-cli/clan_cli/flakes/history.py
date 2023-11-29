# !/usr/bin/env python3
import argparse
from pathlib import Path

from clan_cli.dirs import user_history_file


def list_history() -> list[Path]:
    if not user_history_file().exists():
        return []
    # read path lines from history file
    with open(user_history_file()) as f:
        lines = f.readlines()
    return [Path(line.strip()) for line in lines]


def list_history_command(args: argparse.Namespace) -> None:
    for path in list_history():
        print(path)


# takes a (sub)parser and configures it
def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_history_command)
