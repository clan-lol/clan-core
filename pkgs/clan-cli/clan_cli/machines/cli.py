# !/usr/bin/env python3
import argparse

from .create import register_create_parser
from .delete import register_delete_parser
from .hardware import register_update_hardware_config
from .install import register_install_parser
from .list import register_list_parser
from .morph import register_morph_parser
from .update import register_update_parser


# takes a (sub)parser and configures it
def register_parser(parser: argparse.ArgumentParser) -> None:
    subparser = parser.add_subparsers(
        title="command",
        description="the command to run",
        help="the command to run",
        required=True,
        # Workaround https://github.com/python/cpython/issues/67037 by setting
        # `metavar` to ensure `morph` isn't mentioned
        metavar="{update,create,delete,list,update-hardware-config,install}",
    )

    update_parser = subparser.add_parser(
        "update",
        help="Update one or more machines",
        epilog=(
            """
This subcommand provides an interface to update machines managed by Clan.

Examples:

  $ clan machines update [MACHINES]
  Will update the specified machines [MACHINES], if [MACHINES] is omitted, the command
  will attempt to update every configured machine.
  To exclude machines being updated `clan.core.deployment.requireExplicitUpdate = true;`
  can be set in the machine config.

  $ clan machines update --tags [TAGS..]
  Will update all machines that have the specified tags associated through the inventory.
  If multiple tags are specified machines are matched against both tags.

  $ clan machines update --tags vm
  Will update all machines that are associated with the "vm" tag through the inventory.

  $ clan machines update machine1 machine2 --tags production
  Will update only machine1 and machine2 if they both have the "production" tag.

For more detailed information, visit: https://docs.clan.lol/guides/getting-started/update
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    register_update_parser(update_parser)

    create_parser = subparser.add_parser("create", help="Create a machine")
    register_create_parser(create_parser)

    delete_parser = subparser.add_parser("delete", help="Delete a machine")
    register_delete_parser(delete_parser)

    # Don't set `help` so that it doesn't show up in `clan machines --help`
    morph_parser = subparser.add_parser("morph")
    register_morph_parser(morph_parser)

    list_parser = subparser.add_parser(
        "list",
        help="List machines",
        epilog=(
            """
This subcommand lists all machines managed by this clan.

Examples:

  $ clan machines list
  Lists all the machines and their descriptions.

  $ clan machines list --tags [TAGS..]
  Lists all the machines that have the specified tags associated through the inventory.
  If multiple tags are specified machines are matched against both tags.

  $ clan machines list --tags vm
  Lists all machines that are associated with the "vm" tag through the inventory.
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    register_list_parser(list_parser)

    update_hardware_config_parser = subparser.add_parser(
        "update-hardware-config",
        help="Generate hardware specifics for a machine",
        description="""
Generates hardware specifics for a machine. Such as the host platform, available kernel modules, etc.

The target must be a Linux based system reachable via SSH.
        """,
        epilog=(
            """
Examples:

  $ clan machines update-hardware-config [MACHINE] [TARGET_HOST]
  Will generate hardware specifics for the the specified `[TARGET_HOST]` and place the result in hardware.nix for the given machine `[MACHINE]`.

For more detailed information, visit: https://docs.clan.lol/guides/getting-started/configure/#machine-configuration

"""
        ),
    )
    register_update_hardware_config(update_hardware_config_parser)

    install_parser = subparser.add_parser(
        "install",
        help="Install a machine",
        description="""
Install a configured machine over the network.
The target must be a Linux based system reachable via SSH.
Installing a machine means overwriting the target's disk.
        """,
        epilog=(
            """
This subcommand provides an interface to install machines managed by Clan.

Examples:

  $ clan machines install [MACHINE] --target-host [TARGET_HOST]
  Will install the specified machine [MACHINE] to the specified [TARGET_HOST].
  If the `--target-host` flag is omitted will try to find host information by
  checking the deployment configuration inside the specified machine.

  $ clan machines install [MACHINE] --json [JSON]
  Will install the specified machine [MACHINE] to the host exposed by
  the deployment information of the [JSON] deployment string.

For information on how to set up the installer see: https://docs.clan.lol/guides/getting-started/create-installer/
For more detailed information, visit: https://docs.clan.lol/guides/getting-started/hardware-report-physical
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    register_install_parser(install_parser)
