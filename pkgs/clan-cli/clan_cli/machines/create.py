import argparse

from .folders import machine_folder


def create_command(args: argparse.Namespace) -> None:
    folder = machine_folder(args.host)
    folder.mkdir(parents=True, exist_ok=True)


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("host", type=str)
    parser.set_defaults(func=create_command)
