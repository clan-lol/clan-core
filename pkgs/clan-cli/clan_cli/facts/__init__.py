# !/usr/bin/env python3
import argparse

from .check import register_check_parser
from .generate import register_generate_parser
from .list import register_list_parser
from .upload import register_upload_parser


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
    )

    check_parser = subparser.add_parser("check", help="check if facts are up to date")
    register_check_parser(check_parser)

    list_parser = subparser.add_parser("list", help="list all facts")
    register_list_parser(list_parser)

    parser_generate = subparser.add_parser(
        "generate",
        help="generate public and secret facts for machines",
        epilog=(
            """
This subcommand allows control of the generation of facts.
Often this function will be invoked automatically on deploying machines,
but there are situations the user may want to have more granular control,
especially for the regeneration of certain services.

A service is an included clan-module that implements facts generation functionality.
For example the zerotier module will generate private and public facts.
In this case the public fact will be the resulting zerotier-ip of the machine.
The secret fact will be the zerotier-identity-secret, which is used by zerotier
to prove the machine has control of the zerotier-ip.


Examples:

  $ clan facts generate
  Will generate facts for all machines.
   
  $ clan facts generate [MACHINE]
  Will generate facts for the specified machine.

  $ clan facts generate [MACHINE] --service [SERVICE]
  Will generate facts for the specified machine for the specified service.

  $ clan facts generate --service [SERVICE] --regenerate
  Will regenerate facts, if they are already generated for a specific service.
  This is especially useful for resetting certain passwords while leaving the rest
  of the facts for a machine in place.

For more detailed information, visit: https://docs.clan.lol/getting-started/secrets/
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    register_generate_parser(parser_generate)

    parser_upload = subparser.add_parser("upload", help="upload secrets for machines")
    register_upload_parser(parser_upload)
