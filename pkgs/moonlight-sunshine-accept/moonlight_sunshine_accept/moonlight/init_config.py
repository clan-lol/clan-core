import argparse

from .state import init_state


def read_file(file_path: str) -> str:
    with open(file_path) as file:
        return file.read()


def init_config(args: argparse.Namespace) -> None:
    key = read_file(args.key)
    certificate = read_file(args.certificate)

    init_state(certificate, key)
    print("Finished initializing moonlight state.")


def register_config_initialization_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--certificate")
    parser.add_argument("--key")
    parser.set_defaults(func=init_config)
