import argparse
import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from clan_lib.api import API
from clan_lib.cmd import RunOpts, run
from clan_lib.dirs import specific_machine_dir
from clan_lib.errors import ClanCmdError, ClanError
from clan_lib.git import commit_file
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_config, nix_eval
from clan_lib.ssh.remote import HostKeyCheck, Remote

from clan_cli.completions import add_dynamic_completer, complete_machines

from .types import machine_name_type

log = logging.getLogger(__name__)


class HardwareConfig(Enum):
    NIXOS_FACTER = "nixos-facter"
    NIXOS_GENERATE_CONFIG = "nixos-generate-config"
    NONE = "none"

    def config_path(self, machine: Machine) -> Path:
        machine_dir = specific_machine_dir(machine)
        if self == HardwareConfig.NIXOS_FACTER:
            return machine_dir / "facter.json"
        return machine_dir / "hardware-configuration.nix"

    @classmethod
    def detect_type(cls: type["HardwareConfig"], machine: Machine) -> "HardwareConfig":
        hardware_config = HardwareConfig.NIXOS_GENERATE_CONFIG.config_path(machine)

        if hardware_config.exists() and "throw" not in hardware_config.read_text():
            return HardwareConfig.NIXOS_GENERATE_CONFIG

        if HardwareConfig.NIXOS_FACTER.config_path(machine).exists():
            return HardwareConfig.NIXOS_FACTER

        return HardwareConfig.NONE


@API.register
def show_machine_hardware_config(machine: Machine) -> HardwareConfig:
    """
    Show hardware information for a machine returns None if none exist.
    """
    return HardwareConfig.detect_type(machine)


@API.register
def show_machine_hardware_platform(machine: Machine) -> str | None:
    """
    Show hardware information for a machine returns None if none exist.
    """
    config = nix_config()
    system = config["system"]
    cmd = nix_eval(
        [
            f"{machine.flake}#clanInternals.machines.{system}.{machine.name}",
            "--apply",
            "machine: { inherit (machine.pkgs) system; }",
            "--json",
        ]
    )
    proc = run(cmd, RunOpts(prefix=machine.name))
    res = proc.stdout.strip()

    host_platform = json.loads(res)
    return host_platform.get("system", None)


@dataclass
class HardwareGenerateOptions:
    machine: Machine
    backend: HardwareConfig
    password: str | None = None


@API.register
def generate_machine_hardware_info(
    opts: HardwareGenerateOptions, target_host: Remote
) -> HardwareConfig:
    """
    Generate hardware information for a machine
    and place the resulting *.nix file in the machine's directory.
    """

    machine = opts.machine

    hw_file = opts.backend.config_path(opts.machine)
    hw_file.parent.mkdir(parents=True, exist_ok=True)

    if opts.backend == HardwareConfig.NIXOS_FACTER:
        config_command = ["nixos-facter"]
    else:
        config_command = [
            "nixos-generate-config",
            # Filesystems are managed by disko
            "--no-filesystems",
            "--show-hardware-config",
        ]

    with target_host.ssh_control_master() as ssh, ssh.become_root() as sudo_ssh:
        out = sudo_ssh.run(config_command, opts=RunOpts(check=False))
    if out.returncode != 0:
        if "nixos-facter" in out.stderr and "not found" in out.stderr:
            machine.error(str(out.stderr))
            msg = (
                "Please use our custom nixos install images from https://github.com/nix-community/nixos-images/releases/tag/nixos-unstable. "
                "nixos-factor only works on nixos / clan systems currently."
            )
            raise ClanError(msg)

        machine.error(str(out))
        msg = f"Failed to inspect {opts.machine}. Address: {target_host.target}"
        raise ClanError(msg)

    backup_file = None
    if hw_file.exists():
        backup_file = hw_file.with_suffix(".bak")
        hw_file.replace(backup_file)
    hw_file.write_text(out.stdout)
    print(f"Successfully generated: {hw_file}")

    # try to evaluate the machine
    # If it fails, the hardware-configuration.nix file is invalid

    commit_file(
        hw_file,
        opts.machine.flake.path,
        f"machines/{opts.machine}/{hw_file.name}: update hardware configuration",
    )
    try:
        show_machine_hardware_platform(opts.machine)
        if backup_file:
            backup_file.unlink(missing_ok=True)
    except ClanCmdError as e:
        log.exception("Failed to evaluate hardware-configuration.nix")
        # Restore the backup file
        print(f"Restoring backup file {backup_file}")
        if backup_file:
            backup_file.replace(hw_file)
        # TODO: Undo the commit

        msg = "Invalid hardware-configuration.nix file"
        raise ClanError(
            msg,
            description=f"Configuration at '{hw_file}' is invalid. Please check the file and try again.",
        ) from e

    return opts.backend


def update_hardware_config_command(args: argparse.Namespace) -> None:
    host_key_check = HostKeyCheck.from_str(args.host_key_check)
    machine = Machine(flake=args.flake, name=args.machine)
    opts = HardwareGenerateOptions(
        machine=machine,
        password=args.password,
        backend=HardwareConfig(args.backend),
    )

    if args.target_host:
        target_host = Remote.from_deployment_address(
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
