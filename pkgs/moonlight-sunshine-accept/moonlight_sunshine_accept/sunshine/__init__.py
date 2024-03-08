import argparse

from .init_certificates import register_initialization_parser
from .init_state import register_state_initialization_parser
from .listen import register_socket_listener


def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )

    subparser.add_parser(
        "generate",
        # title="command",
        aliases=["gen"],
        description="Generate a shareable link",
        help="Generate a shareable link",
    )
    # TODO: add a timeout for the link
    # generate.add_argument(
    #     "--timeout",
    #     default="10",
    # )
    # copy = subparsers.add_parser("copy", description="Copy the link to the clipboard")

    initialization_parser = subparser.add_parser(
        "init",
        aliases=["i"],
        description="Initialize the sunshine credentials",
        help="Initialize the sunshine credentials",
    )
    register_initialization_parser(initialization_parser)

    state_initialization_parser = subparser.add_parser(
        "init-state",
        description="Initialize the sunshine state file",
        help="Initialize the sunshine state file",
    )
    register_state_initialization_parser(state_initialization_parser)

    listen_parser = subparser.add_parser(
        "listen",
        description="Listen for incoming connections",
        help="Listen for incoming connections",
    )
    register_socket_listener(listen_parser)

    # TODO: Add a machine directly <- useful when using dependent secrets
    # sunshine_add = subparser.add_parser(
    #     "add",
    #     aliases=["a"],
    #     description="Add a new moonlight machine to sunshine",
    #     help="Add a new moonlight machine to sunshine",
    # )
    # sunshine_add.add_argument("--url", type=str, help="URL of the moonlight machine")
    # sunshine_add.add_argument(
    #     "--cert", type=str, help="Certificate of the moonlight machine"
    # )
    # sunshine_add.add_argument("--uuid", type=str, help="UUID of the moonlight machine")
