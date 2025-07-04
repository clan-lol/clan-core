"""Common argument types and utilities for host key checking in clan CLI commands."""

import argparse

from clan_lib.ssh.host_key import HostKeyCheck


def host_key_check_type(value: str) -> HostKeyCheck:
    """
    Argparse type converter for HostKeyCheck enum.
    """
    try:
        return HostKeyCheck(value)
    except ValueError:
        valid_values = [e.value for e in HostKeyCheck]
        msg = f"Invalid host key check mode: {value}. Valid options: {', '.join(valid_values)}"
        raise argparse.ArgumentTypeError(msg) from None


def add_host_key_check_arg(
    parser: argparse.ArgumentParser, default: HostKeyCheck = HostKeyCheck.ASK
) -> None:
    parser.add_argument(
        "--host-key-check",
        type=host_key_check_type,
        default=default,
        help=f"Host key (.ssh/known_hosts) check mode. Options: {', '.join([e.value for e in HostKeyCheck])}",
    )
