import argparse

from .init_certificates import register_initialization_parser
from .init_config import register_config_initialization_parser
from .join import register_join_parser


def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )

    initialization_parser = subparser.add_parser(
        "init",
        aliases=["i"],
        description="Initialize the moonlight credentials",
        help="Initialize the moonlight credentials",
    )
    register_initialization_parser(initialization_parser)

    config_initialization_parser = subparser.add_parser(
        "init-config",
        description="Initialize the moonlight configuration",
        help="Initialize the moonlight configuration",
    )
    register_config_initialization_parser(config_initialization_parser)

    join_parser = subparser.add_parser(
        "join",
        aliases=["j"],
        description="Join a sunshine host",
        help="Join a sunshine host",
    )
    register_join_parser(join_parser)
