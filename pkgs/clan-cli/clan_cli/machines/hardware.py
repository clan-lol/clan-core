import argparse
import logging
from pathlib import Path
from typing import get_args

from clan_lib.flake import require_flake
from clan_lib.machines.hardware import (
    HardwareConfig,
    HardwareGenerateOptions,
    run_machine_hardware_info,
)
from clan_lib.machines.machines import Machine
from clan_lib.machines.suggestions import validate_machine_names
from clan_lib.ssh.host_key import HostKeyCheck
from clan_lib.ssh.remote import Remote

from clan_cli.completions import add_dynamic_completer, complete_machines

from .types import machine_name_type

log = logging.getLogger(__name__)


def update_hardware_config_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    validate_machine_names([args.machine], flake)
    machine = Machine(flake=flake, name=args.machine)
    opts = HardwareGenerateOptions(
        machine=machine,
        password=args.password,
        backend=HardwareConfig(args.backend),
    )

    if args.target_host:
        target_host = Remote.from_ssh_uri(
            machine_name=machine.name, address=args.target_host
        )
    else:
        target_host = machine.target_host()

    target_host = target_host.override(
        host_key_check=args.host_key_check, private_key=args.identity_file
    )

    run_machine_hardware_info(opts, target_host)


def register_update_hardware_config(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=update_hardware_config_command)
    machine_parser = parser.add_argument(
        "machine",
        help="the name of the machine",
        type=machine_name_type,
    )
    add_dynamic_completer(machine_parser, complete_machines)
    parser.add_argument(
        "target_host",
        type=str,
        nargs="?",
        help="ssh address to install to in the form of user@host:2222",
    )
    parser.add_argument(
        "--host-key-check",
        choices=list(get_args(HostKeyCheck)),
        default="ask",
        help="Host key (.ssh/known_hosts) check mode.",
    )
    parser.add_argument(
        "--password",
        help="Pre-provided password the cli will prompt otherwise if needed.",
        type=str,
        required=False,
    )
    parser.add_argument(
        "--backend",
        help="The type of hardware report to generate.",
        choices=["nixos-generate-config", "nixos-facter"],
        default="nixos-facter",
    )
    parser.add_argument(
        "-i",
        dest="identity_file",
        type=Path,
        help="specify which SSH private key file to use",
    )
