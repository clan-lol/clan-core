# !/usr/bin/env python3
import argparse

from .add import list_history


def list_history_command(args: argparse.Namespace) -> None:
    for history_entry in list_history():
        print(history_entry.flake.flake_url)


# takes a (sub)parser and configures it
def register_list_parser(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=list_history_command)
