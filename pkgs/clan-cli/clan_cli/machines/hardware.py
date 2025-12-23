import argparse
import logging
from pathlib import Path
from typing import get_args

from clan_lib.flake import require_flake
from clan_lib.machines.hardware import (
    HardwareConfig,
    HardwareGenerateOptions,
    run_machine_hardware_info_init,
    run_machine_hardware_info_update,
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
        kexec=None,  # unlike `init`, we do not kexec on `update`
        backend=HardwareConfig(args.backend),
        debug=args.debug,
    )

    if args.target_host:
        target_host = Remote.from_ssh_uri(
            machine_name=machine.name,
            address=args.target_host,
        )
    else:
        target_host = machine.target_host()

    target_host = target_host.override(
        host_key_check=args.host_key_check,
        private_key=args.identity_file,
    )

    if not args.yes:
        confirm = (
            input(
                f"Update hardware configuration for machine '{machine.name}' at '{target_host.target}'? [y/N]: "
            )
            .strip()
            .lower()
        )
        if confirm not in ("y", "yes"):
            log.info("Aborted.")
            return

    run_machine_hardware_info_update(opts, target_host)


def init_hardware_config_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    validate_machine_names([args.machine], flake)
    machine = Machine(flake=flake, name=args.machine)
    opts = HardwareGenerateOptions(
        machine=machine,
        password=args.password,
        kexec=args.kexec,
        backend=HardwareConfig(args.backend),
        debug=args.debug,
    )

    if args.target_host:
        target_host = Remote.from_ssh_uri(
            machine_name=machine.name,
            address=args.target_host,
        )
    else:
        target_host = machine.target_host()

    target_host = target_host.override(
        host_key_check=args.host_key_check,
        private_key=args.identity_file,
    )

    if not args.yes:
        confirm = (
            input(
                "WARNING: This will reboot the target machine into a temporary NixOS system "
                "to gather hardware information. This may disrupt any services running on the machine. "
                f"Update hardware configuration for machine '{machine.name}' at '{target_host.target}'? [y/N]:"
            )
            .strip()
            .lower()
        )
        if confirm not in ("y", "yes"):
            log.info("Aborted.")
            return

    run_machine_hardware_info_init(opts, target_host)


def register_init_hardware_config(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=init_hardware_config_command)
    machine_parser = parser.add_argument(
        "machine",
        help="the name of the machine",
        type=machine_name_type,
    )
    add_dynamic_completer(machine_parser, complete_machines)
    parser.add_argument(
        "--target-host",
        type=str,
        help="ssh address to install to in the form of user@host:2222",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="do not ask for confirmation.",
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
    parser.add_argument(
        "--kexec",
        type=str,
        help="use another kexec tarball to bootstrap NixOS",
    )


def register_update_hardware_config(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=update_hardware_config_command)
    machine_parser = parser.add_argument(
        "machine",
        help="the name of the machine",
        type=machine_name_type,
    )
    add_dynamic_completer(machine_parser, complete_machines)
    parser.add_argument(
        "--target-host",
        type=str,
        help="ssh address to install to in the form of user@host:2222",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="do not ask for confirmation.",
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
