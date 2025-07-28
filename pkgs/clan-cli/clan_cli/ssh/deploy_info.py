import argparse
import contextlib
import json
import logging
import textwrap
from pathlib import Path
from typing import get_args

from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.network.qr_code import parse_qr_image_to_json, parse_qr_json_to_networks
from clan_lib.network.tor.lib import spawn_tor
from clan_lib.ssh.remote import HostKeyCheck, Remote

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
)

log = logging.getLogger(__name__)


def get_tor_remote(remotes: list[Remote]) -> Remote:
    """Get the Remote configured for SOCKS5 proxy (Tor)."""
    tor_remotes = [r for r in remotes if r.socks_port]

    if not tor_remotes:
        msg = "No socks5 proxy address provided, please provide a socks5 proxy address."
        raise ClanError(msg)

    if len(tor_remotes) > 1:
        msg = "Multiple socks5 proxy addresses provided, expected only one."
        raise ClanError(msg)

    return tor_remotes[0]


def find_reachable_host(remotes: list[Remote]) -> Remote | None:
    # If we only have one address, we have no choice but to use it.
    if len(remotes) == 1:
        return remotes[0]

    for remote in remotes:
        with contextlib.suppress(ClanError):
            remote.check_machine_ssh_reachable()
            return remote
    return None


def ssh_shell_from_remotes(
    remotes: list[Remote], command: list[str] | None = None
) -> None:
    if command and len(command) == 1 and command[0].count(" ") > 0:
        msg = (
            textwrap.dedent("""
            It looks like you quoted the remote command.
            The first argument should be the command to run, not a quoted string.
        """)
            .lstrip("\n")
            .rstrip("\n")
        )
        raise ClanError(msg)

    if host := find_reachable_host(remotes):
        host.interactive_ssh(command)
        return

    log.info("Could not reach host via clearnet addresses")
    log.info("Trying to reach host via tor")

    tor_remotes = [r for r in remotes if r.socks_port]
    if not tor_remotes:
        msg = "No tor address provided, please provide a tor address."
        raise ClanError(msg)

    with spawn_tor():
        for tor_remote in tor_remotes:
            log.info(f"Trying to reach host via tor address: {tor_remote}")

            with contextlib.suppress(ClanError):
                tor_remote.check_machine_ssh_reachable()

                log.info(
                    "Host reachable via tor address, starting interactive ssh session."
                )
                tor_remote.interactive_ssh(command)
                return

        log.error("Could not reach host via tor address.")


def ssh_command_parse(args: argparse.Namespace) -> list[Remote] | None:
    host_key_check = args.host_key_check
    remotes = None

    if args.json:
        json_file = Path(args.json)
        if json_file.is_file():
            data = json.loads(json_file.read_text())
        else:
            data = json.loads(args.json)

        networks = parse_qr_json_to_networks(data, args.flake)
        remotes = []
        for _network_type, network_data in networks.items():
            remote = network_data["remote"]
            remotes.append(remote.override(host_key_check=host_key_check))

    elif args.png:
        data = parse_qr_image_to_json(Path(args.png))
        networks = parse_qr_json_to_networks(data, args.flake)
        remotes = []
        for _network_type, network_data in networks.items():
            remote = network_data["remote"]
            remotes.append(remote.override(host_key_check=host_key_check))

    elif hasattr(args, "machine") and args.machine:
        machine = Machine(args.machine, args.flake)
        target = machine.target_host().override(
            command_prefix=machine.name, host_key_check=host_key_check
        )
        remotes = [target]
    else:
        return None

    ssh_options = None
    if hasattr(args, "ssh_option") and args.ssh_option:
        ssh_options = {}
        for name, value in args.ssh_option:
            ssh_options[name] = value

    if ssh_options:
        remotes = [remote.override(ssh_options=ssh_options) for remote in remotes]

    return remotes


def ssh_command(args: argparse.Namespace) -> None:
    remotes = ssh_command_parse(args)
    if not remotes:
        msg = "No MACHINE, --json or --png data provided"
        raise ClanError(msg)
    ssh_shell_from_remotes(remotes, args.remote_command)


def register_parser(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "machine",
        type=str,
        nargs="?",
        metavar="MACHINE",
        help="Machine to ssh into (uses clan.core.networking.targetHost from configuration).",
    )

    group.add_argument(
        "-j",
        "--json",
        type=str,
        help=(
            "Deployment information as a JSON string or path to a JSON file "
            "(generated by starting the clan installer)."
        ),
    )
    group.add_argument(
        "-P",
        "--png",
        type=str,
        help="Deployment information as a QR code image file (generated by starting the clan installer).",
    )

    parser.add_argument(
        "--host-key-check",
        choices=list(get_args(HostKeyCheck)),
        default="tofu",
        help="Host key (.ssh/known_hosts) check mode.",
    )

    parser.add_argument(
        "--ssh-option",
        help="SSH option to set (can be specified multiple times)",
        nargs=2,
        metavar=("name", "value"),
        action="append",
        default=[],
    )

    parser.add_argument(
        "-c",
        "--remote-command",
        type=str,
        metavar="COMMAND",
        nargs=argparse.REMAINDER,
        help="Command to execute on the remote host, needs to be the LAST argument as it takes all remaining arguments.",
    )

    add_dynamic_completer(
        parser._actions[1],  # noqa: SLF001
        complete_machines,
    )  # assumes 'machine' is the first positional

    parser.set_defaults(func=ssh_command)
