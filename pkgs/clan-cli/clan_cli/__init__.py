import argparse
import contextlib
import logging
import sys
from pathlib import Path
from types import ModuleType

# These imports are unused, but necessary for @API.register to run once.
from .api import admin, directory, disk, iwd, mdns_discovery, modules
from .arg_actions import AppendOptionAction
from .clan import show, update

# API endpoints that are not used in the cli.
__all__ = ["admin", "directory", "disk", "iwd", "mdns_discovery", "modules", "update"]

from . import (
    backups,
    clan,
    history,
    secrets,
    select,
    state,
    vms,
)
from .custom_logger import setup_logging
from .dirs import get_clan_flake_toplevel_or_env
from .errors import ClanError
from .facts import cli as facts
from .flake import Flake
from .flash import cli as flash_cli
from .hyperlink import help_hyperlink
from .machines import cli as machines
from .profiler import profile
from .ssh import deploy_info as ssh_cli
from .vars import cli as vars_cli

log = logging.getLogger(__name__)

argcomplete: ModuleType | None = None
with contextlib.suppress(ImportError):
    import argcomplete  # type: ignore[no-redef]


def flake_path(arg: str) -> Flake:
    flake_dir = Path(arg).resolve()
    if flake_dir.exists() and flake_dir.is_dir():
        return Flake(str(flake_dir))
    return Flake(arg)


def default_flake() -> Flake | None:
    val = get_clan_flake_toplevel_or_env()
    if val:
        return Flake(str(val))
    return None


def add_common_flags(parser: argparse.ArgumentParser) -> None:
    def argument_exists(parser: argparse.ArgumentParser, arg: str) -> bool:
        """
        Check if an argparse argument already exists.
        This is needed because the aliases subcommand doesn't *really*
        create an alias - it duplicates the actual parser in the tree
        making duplication inevitable while naively traversing.

        The error that would be thrown by argparse:
        - argparse.ArgumentError
        """
        return any(arg in action.option_strings for action in parser._actions)  # noqa: SLF001 -> private_member accessed

    if not argument_exists(parser, "--debug"):
        parser.add_argument(
            "--debug",
            help="Enable debug logging",
            action="store_true",
            default=False,
        )

    if not argument_exists(parser, "--option"):
        parser.add_argument(
            "--option",
            help="Nix option to set",
            nargs=2,
            metavar=("name", "value"),
            action=AppendOptionAction,
            default=[],
        )

    if not argument_exists(parser, "--flake"):
        parser.add_argument(
            "--flake",
            help="path to the flake where the clan resides in, can be a remote flake or local, can be set through the [CLAN_DIR] environment variable",
            default=default_flake(),
            metavar="PATH",
            type=flake_path,
        )


def register_common_flags(parser: argparse.ArgumentParser) -> None:
    has_subparsers = False
    for action in parser._actions:  # noqa: SLF001
        if isinstance(action, argparse._SubParsersAction):  # noqa: SLF001
            for _choice, child_parser in action.choices.items():
                has_subparsers = True
                register_common_flags(child_parser)

    if not has_subparsers:
        add_common_flags(parser)


def create_parser(prog: str | None = None) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=prog,
        usage="%(prog)s [-h] [SUBCOMMAND]",
        description="The clan cli tool",
        epilog=(
            f"""
Online reference for the clan cli tool: {help_hyperlink("cli reference", "https://docs.clan.lol/reference/cli/")}
For more detailed information, visit: {help_hyperlink("docs", "https://docs.clan.lol")}
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    subparsers = parser.add_subparsers()

    show_parser = subparsers.add_parser(
        "show",
        help="Show meta information about the clan",
        description="Show meta information about the clan",
        epilog=(
            """
This command prints the metadata of a clan.

Examples:

  $ clan show --flake [PATH]
  Name: My Empty Clan
  Description: some nice description
  Icon: A path to the png

Note: The meta results from clan/meta.json and manual flake arguments.
      It may not be present for clans not created via the clan-app.
"""
        ),
    )
    show_parser.set_defaults(func=show.show_command)

    parser_backups = subparsers.add_parser(
        "backups",
        aliases=["b"],
        help="Manage backups of clan machines",
        description="Manage backups of clan machines",
        epilog=(
            f"""
This subcommand provides an interface to backups that clan machines expose.

Examples:

  $ clan backups list [MACHINE]
  List backups for the machine [MACHINE]

  $ clan backups create [MACHINE]
  Create a backup for the machine [MACHINE].

  $ clan backups restore [MACHINE] [PROVIDER] [NAME]
  The backup to restore for the machine [MACHINE] with the configured [PROVIDER]
  with the name [NAME].

For more detailed information visit: {help_hyperlink("backups", "https://docs.clan.lol/getting-started/backups")}.
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    backups.register_parser(parser_backups)

    parser_flake = subparsers.add_parser(
        "flakes",
        aliases=["f"],
        help="Create a clan flake inside the current directory",
        description="Create a clan flake inside the current directory",
        epilog=(
            f"""
Examples:
  $ clan flakes create [DIR]
  Will create a new clan flake in the specified directory and create it if it
  doesn't exist yet. The flake will be created from a default template.

For more detailed information, visit: {help_hyperlink("getting-started", "https://docs.clan.lol/getting-started")}
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )

    clan.register_parser(parser_flake)

    parser_flash = subparsers.add_parser(
        "flash",
        help="Flashes your machine to an USB drive",
        description="Flashes your machine to an USB drive",
        epilog=(
            f"""
Examples:
  $ clan flash write mymachine --disk main /dev/sd<X> --ssh-pubkey ~/.ssh/id_rsa.pub
  Will flash the machine 'mymachine' to the disk '/dev/sd<X>' with the ssh public key '~/.ssh/id_rsa.pub'.

For more detailed information, visit: {help_hyperlink("getting-started", "https://docs.clan.lol/getting-started/installer")}
            """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    flash_cli.register_parser(parser_flash)

    parser_ssh = subparsers.add_parser(
        "ssh",
        help="Ssh to a remote machine",
        description="Ssh to a remote machine",
        epilog=(
            f"""
This subcommand allows seamless ssh access to the nixos-image builders or a machine of your clan.

Examples:

  $ clan ssh [ssh_args ...] berlin`

  Will ssh in to the machine called `berlin`, using the
  `clan.core.networking.targetHost` specified in its configuration

  $ clan ssh [ssh_args ...] --json [JSON]
  Will ssh in to the machine based on the deployment information contained in
  the json string. [JSON] can either be a json formatted string itself, or point
  towards a file containing the deployment information

For more detailed information, visit: {help_hyperlink("deploy", "https://docs.clan.lol/getting-started/deploy")}
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    ssh_cli.register_parser(parser_ssh)

    parser_secrets = subparsers.add_parser(
        "secrets",
        help="Manage secrets",
        description="Manage secrets",
        epilog=(
            f"""
This subcommand provides an interface to secrets.

Examples:

  $ clan secrets list [regex]
  Will list secrets for all managed machines.
  It accepts an optional regex, allowing easy filtering of returned secrets.

  $ clan secrets get [SECRET]
  Will display the content of the specified secret.

For more detailed information, visit: {help_hyperlink("secrets", "https://docs.clan.lol/getting-started/secrets")}
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    secrets.register_parser(parser_secrets)

    parser_facts = subparsers.add_parser(
        "facts",
        help="Manage facts",
        description="Manage facts",
        epilog=(
            f"""

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

For more detailed information, visit: {help_hyperlink("secrets", "https://docs.clan.lol/getting-started/secrets")}
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    facts.register_parser(parser_facts)

    # like facts but with vars instead of facts
    parser_vars = subparsers.add_parser(
        "vars",
        aliases=["va"],
        help="Manage vars",
        description="Manage vars",
        epilog=(
            f"""
This subcommand provides an interface to `vars` of clan machines.
Vars are variables that a service can generate.
There are public and secret vars.
Public vars can be referenced by other machines directly.
Public vars can include: ip addresses, public keys.
Secret vars can include: passwords, private keys.

A service is an included clan-module that implements vars generation functionality.
For example the zerotier module will generate private and public vars.
In this case the public var will be the resulting zerotier-ip of the machine.
The secret var will be the zerotier-identity-secret, which is used by zerotier
to prove the machine has control of the zerotier-ip.

Examples:

    $ clan vars generate
    Will generate vars for all machines.

    $ clan vars generate --service [SERVICE] --regenerate
    Will regenerate vars, if they are already generated for a specific service.
    This is especially useful for resetting certain passwords while leaving the rest
    of the vars for a machine in place.

For more detailed information, visit: {help_hyperlink("secrets", "https://docs.clan.lol/getting-started/secrets")}
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    vars_cli.register_parser(parser_vars)

    parser_machine = subparsers.add_parser(
        "machines",
        aliases=["m"],
        help="Manage machines and their configuration",
        description="Manage machines and their configuration",
        epilog=(
            f"""
This subcommand provides an interface to machines managed by Clan.

Examples:

  $ clan machines list
  List all the machines managed by Clan.

  $ clan machines update [MACHINES]
  Will update the specified machines [MACHINES], if [MACHINES] is omitted, the command
  will attempt to update every configured machine.

  $ clan machines install [MACHINE] --target-host [TARGET_HOST]
  Will install the specified machine [MACHINE] to the specified [TARGET_HOST].
  If the `--target-host` flag is omitted will try to find host information by
  checking the deployment configuration inside the specified machine.

For more detailed information, visit: {help_hyperlink("deploy", "https://docs.clan.lol/getting-started/deploy")}
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    machines.register_parser(parser_machine)

    parser_vms = subparsers.add_parser(
        "vms", help="Manage virtual machines", description="Manage virtual machines"
    )
    vms.register_parser(parser_vms)

    parser_history = subparsers.add_parser(
        "history",
        description="manage history",
    )
    history.register_parser(parser_history)

    parser_select = subparsers.add_parser(
        "select",
        aliases=["se"],
        help="Select nixos values from the flake",
        description="Select nixos values from the flake",
        epilog=(
            """
This subcommand provides an interface nix values defined in the flake.

Examples:

  $ clan select nixosConfigurations.*.config.networking.hostName
    List hostnames of all nixos configurations as JSON.

  $ clan select nixosConfigurations.{jon,alice}.config.clan.core.vars.generators.*.name
    List all vars generators for jon and alice.

  $ clan select nixosConfigurations.jon.config.envirnonment.systemPackages.1
    List the first system package for jon.
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    select.register_parser(parser_select)

    parser_state = subparsers.add_parser(
        "state",
        aliases=["st"],
        help="Query state information about machines",
        description="Query state information about machines",
        epilog=(
            f"""
This subcommand provides an interface to the state managed by Clan.

State can be folders and databases that modules depend on managed by Clan.

State directories can be added to on a per machine basis:
```
  config.clan.core.state.[SERVICE_NAME].folders = [
    "/home"
    "/root"
  ];
```
Here [SERVICE_NAME] can be set freely, if the user sets them extra `userdata`
can be a good choice.

Examples:

  $ clan state list [MACHINE]
  List state of the machines managed by Clan.

For more detailed information, visit: {help_hyperlink("getting-started", "https://docs.clan.lol/backups")}
        """
        ),
        formatter_class=argparse.RawTextHelpFormatter,
    )
    state.register_parser(parser_state)

    if argcomplete:
        argcomplete.autocomplete(parser, exclude=["morph"])

    register_common_flags(parser)

    return parser


# this will be the entrypoint under /bin/clan (see pyproject.toml config)
@profile
def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()

    if debug := getattr(args, "debug", False):
        setup_logging(logging.DEBUG, root_log_name=__name__.split(".")[0])
        log.debug("Debug log activated")
    else:
        setup_logging(logging.INFO, root_log_name=__name__.split(".")[0])

    if not hasattr(args, "func"):
        return

    try:
        args.func(args)
    except ClanError as e:
        if debug:
            log.exception("Exited with error")
        else:
            log.error("%s", e)
        sys.exit(1)
    except KeyboardInterrupt as ex:
        log.warning("Interrupted by user", exc_info=ex)
        sys.exit(1)


if __name__ == "__main__":
    main()
