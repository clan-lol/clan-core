import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path
from types import ModuleType
from typing import Any

# These imports are unused, but necessary for @API.register to run once.
from clan_cli.api import directory
from clan_cli.flakes import show

__all__ = ["directory"]

from . import (
    backups,
    config,
    facts,
    flakes,
    flash,
    flatpak,
    history,
    machines,
    secrets,
    vms,
)
from .custom_logger import setup_logging
from .dirs import get_clan_flake_toplevel_or_env
from .errors import ClanCmdError, ClanError
from .profiler import profile
from .ssh import cli as ssh_cli

log = logging.getLogger(__name__)

argcomplete: ModuleType | None = None
try:
    import argcomplete  # type: ignore[no-redef]
except ImportError:
    pass


class AppendOptionAction(argparse.Action):
    def __init__(self, option_strings: str, dest: str, **kwargs: Any) -> None:
        super().__init__(option_strings, dest, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[str] | None,
        option_string: str | None = None,
    ) -> None:
        lst = getattr(namespace, self.dest)
        lst.append("--option")
        assert isinstance(values, list), "values must be a list"
        lst.append(values[0])
        lst.append(values[1])


def flake_path(arg: str) -> str | Path:
    flake_dir = Path(arg).resolve()
    if flake_dir.exists() and flake_dir.is_dir():
        return flake_dir
    return arg


def add_common_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--debug",
        help="Enable debug logging",
        action="store_true",
        default=False,
    )

    parser.add_argument(
        "--option",
        help="Nix option to set",
        nargs=2,
        metavar=("name", "value"),
        action=AppendOptionAction,
        default=[],
    )

    parser.add_argument(
        "--flake",
        help="path to the flake where the clan resides in, can be a remote flake or local, can be set through the [CLAN_DIR] environment variable",
        default=get_clan_flake_toplevel_or_env(),
        metavar="PATH",
        type=flake_path,
    )


def register_common_flags(parser: argparse.ArgumentParser) -> None:
    has_subparsers = False
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for choice, child_parser in action.choices.items():
                has_subparsers = True
                register_common_flags(child_parser)
    if not has_subparsers:
        add_common_flags(parser)


def create_parser(prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        description="The clan cli tool.",
        epilog=(
            """
Online reference for the clan cli tool: https://docs.clan.lol/reference/cli/
For more detailed information, visit: https://docs.clan.lol
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = parser.add_subparsers()

    # Commands directly under the root i.e. "clan show"
    show_parser = subparsers.add_parser(
        "show",
        help="Show meta about the clan if present.",
        description="Show meta about the clan if present.",
        epilog=(
            """
This command prints the metadata of a clan.

Examples:

  $ clan show --flake [PATH]
  Name: My Empty Clan
  Description: some nice description
  Icon: A path to the png

Note: The meta results from clan/meta.json and manual flake arguments. It may not be present for clans not created via the clan-app.

"""
        ),
    )
    show_parser.set_defaults(func=show.show_command)

    parser_backups = subparsers.add_parser(
        "backups",
        help="manage backups of clan machines",
        description="manage backups of clan machines",
        epilog=(
            """
This subcommand provides an interface to backups that clan machines expose.

Examples:

  $ clan backups list [MACHINE]
  List backups for the machine [MACHINE]

  $ clan backups create [MACHINE]
  Create a backup for the machine [MACHINE].

  $ clan backups restore [MACHINE] [PROVIDER] [NAME]
  The backup to restore for the machine [MACHINE] with the configured [PROVIDER]
  with the name [NAME].

For more detailed information, visit: https://docs.clan.lol/getting-started/backups/
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    backups.register_parser(parser_backups)

    parser_flake = subparsers.add_parser(
        "flakes",
        help="create a clan flake inside the current directory",
        description="create a clan flake inside the current directory",
        epilog=(
            """
Examples:
  $ clan flakes create [DIR]
  Will create a new clan flake in the specified directory and create it if it
  doesn't exist yet. The flake will be created from a default template.

For more detailed information, visit: https://docs.clan.lol/getting-started
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    flakes.register_parser(parser_flake)

    parser_config = subparsers.add_parser(
        "config",
        help="read a nixos configuration option",
        description="read a nixos configuration option",
        epilog=(
            """
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    config.register_parser(parser_config)

    parser_ssh = subparsers.add_parser(
        "ssh",
        help="ssh to a remote machine",
        description="ssh to a remote machine",
        epilog=(
            """
This subcommand allows seamless ssh access to the nixos-image builders.

Examples:

  $ clan ssh [ssh_args ...] --json [JSON]
  Will ssh in to the machine based on the deployment information contained in
  the json string. [JSON] can either be a json formatted string itself, or point
  towards a file containing the deployment information

For more detailed information, visit: https://docs.clan.lol/getting-started/deploy
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    ssh_cli.register_parser(parser_ssh)

    parser_secrets = subparsers.add_parser(
        "secrets",
        help="manage secrets",
        description="manage secrets",
        epilog=(
            """
This subcommand provides an interface to secret facts.

Examples:

  $ clan secrets list [regex]
  Will list secrets for all managed machines.
  It accepts an optional regex, allowing easy filtering of returned secrets.

  $ clan secrets get [SECRET]
  Will display the content of the specified secret.

For more detailed information, visit: https://docs.clan.lol/getting-started/secrets/
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    secrets.register_parser(parser_secrets)

    parser_facts = subparsers.add_parser(
        "facts",
        help="manage facts",
        description="manage facts",
        epilog=(
            """

This subcommand provides an interface to facts of clan machines.
Facts are artifacts that a service can generate.
There are public and secret facts.
Public facts can be referenced by other machines directly.
Public facts can include: ip addresses, public keys.
Secret facts can include: passwords, private keys.

A service is an included clan-module that implements facts generation functionality.
For example the zerotier module will generate private and public facts.
In this case the public fact will be the resulting zerotier-ip of the machine.
The secret fact will be the zerotier-identity-secret, which is used by zerotier
to prove the machine has control of the zerotier-ip.

Examples:

  $ clan facts generate
  Will generate facts for all machines.

  $ clan facts generate --service [SERVICE] --regenerate
  Will regenerate facts, if they are already generated for a specific service.
  This is especially useful for resetting certain passwords while leaving the rest
  of the facts for a machine in place.

For more detailed information, visit: https://docs.clan.lol/getting-started/secrets/
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    facts.register_parser(parser_facts)

    parser_machine = subparsers.add_parser(
        "machines",
        help="manage machines and their configuration",
        description="manage machines and their configuration",
        epilog=(
            """
This subcommand provides an interface to machines managed by clan.

Examples:

  $ clan machines list
  List all the machines managed by clan.

  $ clan machines update [MACHINES]
  Will update the specified machine [MACHINE], if [MACHINE] is omitted, the command
  will attempt to update every configured machine.

  $ clan machines install [MACHINES] [TARGET_HOST]
  Will install the specified machine [MACHINE], to the specified [TARGET_HOST].

For more detailed information, visit: https://docs.clan.lol/getting-started/deploy
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    machines.register_parser(parser_machine)

    parser_vms = subparsers.add_parser(
        "vms", help="manage virtual machines", description="manage virtual machines"
    )
    vms.register_parser(parser_vms)

    parser_history = subparsers.add_parser(
        "history",
        help="manage history",
        description="manage history",
    )
    history.register_parser(parser_history)

    parser_flash = subparsers.add_parser(
        "flash",
        help="flash machines to usb sticks or into isos",
        description="flash machines to usb sticks or into isos",
    )
    flash.register_parser(parser_flash)

    if argcomplete:
        argcomplete.autocomplete(parser)

    register_common_flags(parser)

    return parser


# this will be the entrypoint under /bin/clan (see pyproject.toml config)
@profile
def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()

    if getattr(args, "debug", False):
        setup_logging(logging.DEBUG, root_log_name=__name__.split(".")[0])
        log.debug("Debug log activated")
        if flatpak.is_flatpak():
            log.debug("Running inside a flatpak sandbox")
    else:
        setup_logging(logging.INFO, root_log_name=__name__.split(".")[0])

    if not hasattr(args, "func"):
        return

    try:
        args.func(args)
    except ClanError as e:
        if args.debug:
            log.exception(e)
            sys.exit(1)
        if isinstance(e, ClanCmdError):
            if e.cmd.msg:
                log.error(e.cmd.msg)
                sys.exit(1)

        log.error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
