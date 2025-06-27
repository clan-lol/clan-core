import argparse
import logging

from clan_lib.machines.hardware import (
    HardwareConfig,
    HardwareGenerateOptions,
    generate_machine_hardware_info,
)
from clan_lib.machines.machines import Machine
from clan_lib.machines.suggestions import validate_machine_names
from clan_lib.ssh.remote import Remote

from clan_cli.completions import add_dynamic_completer, complete_machines

from .types import machine_name_type

log = logging.getLogger(__name__)


def update_hardware_config_command(args: argparse.Namespace) -> None:
    validate_machine_names([args.machine], args.flake)
    host_key_check = args.host_key_check
    machine = Machine(flake=args.flake, name=args.machine)
    opts = HardwareGenerateOptions(
        machine=machine,
        password=args.password,
        backend=HardwareConfig(args.backend),
    )

    if args.target_host:
        target_host = Remote.from_ssh_uri(
            machine_name=machine.name, address=args.target_host
        ).override(host_key_check=host_key_check)
    else:
        target_host = machine.target_host().override(host_key_check=host_key_check)

    generate_machine_hardware_info(opts, target_host)


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
        choices=["strict", "ask", "tofu", "none"],
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
