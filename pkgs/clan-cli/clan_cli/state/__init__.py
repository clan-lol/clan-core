# !/usr/bin/env python3
import argparse

from .list import register_state_parser


def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )

    state_parser = subparser.add_parser(
        "list",
        help="list state folders and the services that configure them",
        description="list state folders and the services that configure them",
        epilog=(
            """
  List state of the machines managed by Clan.

  The backup commands are commands that will exist on the deployed machine.
  They can be introspected by checking under `/run/current-system/sw/bin/[COMMAND]`

  Examples:

  $ clan state list [MACHINE]
  List state of the machine [MACHINE] managed by Clan.


  For more detailed information, visit: https://docs.clan.lol/getting-started/backups/
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    register_state_parser(state_parser)
