# !/usr/bin/env python3
import argparse

from .list import register_list_parser
from .overview import register_overview_parser
from .ping import register_ping_parser


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )

    list_parser = subparser.add_parser(
        "list",
        help="list all networks",
        epilog=(
            """
This subcommand allows listing all networks
```
[NETWORK1] [PRIORITY] [MODULE] [PEER1, PEER2]
[NETOWKR2] [PRIORITY] [MODULE] [PEER1, PEER2]
```

Examples:

  $ clan network list
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    register_list_parser(list_parser)

    ping_parser = subparser.add_parser(
        "ping",
        help="ping a machine to check if it's online",
        epilog=(
            """
This subcommand allows pinging a machine to check if it's online

Examples:

  $ clan network ping machine1
  Check machine1 on all networks (in priority order)

  $ clan network ping machine1 --network tor
  Check machine1 only on the tor network
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    register_ping_parser(ping_parser)

    overview_parser = subparser.add_parser(
        "overview",
        help="show the overview of all network and hosts",
        epilog=(
            """
This command shows the complete state of all networks

Examples:

  $ clan network overview
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    register_overview_parser(overview_parser)
