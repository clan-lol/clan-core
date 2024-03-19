import argparse

from .state import init_state


def init_state_file(args: argparse.Namespace) -> None:
    uuid = args.uuid
    state_file = args.state_file
    init_state(uuid, state_file)
    print("Finished initializing sunshine state file.")


def register_state_initialization_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--uuid")
    parser.add_argument("--state-file")
    parser.set_defaults(func=init_state_file)
