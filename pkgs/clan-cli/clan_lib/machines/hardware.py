import json
import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import TypedDict

from clan_lib.api import API
from clan_lib.cmd import Log, RunOpts, run
from clan_lib.dirs import specific_machine_dir
from clan_lib.errors import ClanCmdError, ClanError
from clan_lib.git import commit_file
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_config, nix_eval, nix_shell
from clan_lib.ssh.create import create_secret_key_nixos_anywhere
from clan_lib.ssh.remote import Remote

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


def get_machine_target_platform(machine: Machine) -> str | None:
    config = nix_config()
    system = config["system"]
    cmd = nix_eval(
        [
            f"{machine.flake}#clanInternals.machines.{system}.{machine.name}",
            "--apply",
            "machine: { inherit (machine.pkgs) system; }",
            "--json",
        ],
    )
    proc = run(cmd, RunOpts(prefix=machine.name))
    res = proc.stdout.strip()

    host_platform = json.loads(res)
    return host_platform.get("system", None)


@dataclass
class HardwareGenerateOptions:
    machine: Machine
    backend: HardwareConfig = HardwareConfig.NIXOS_FACTER
    password: str | None = None


@API.register
def run_machine_hardware_info(
    opts: HardwareGenerateOptions,
    target_host: Remote,
) -> HardwareConfig:
    """Generate hardware information for a machine
    and place the resulting *.nix file in the machine's directory.
    """
    machine = opts.machine

    hw_file = opts.backend.config_path(opts.machine)
    hw_file.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "nixos-anywhere",
        "--flake",
        f"{machine.flake}#{machine.name}",
        "--phases",
        "kexec",
        "--generate-hardware-config",
        str(opts.backend.value),
        str(opts.backend.config_path(machine)),
    ]

    if target_host.private_key:
        cmd += ["--ssh-option", f"IdentityFile={target_host.private_key}"]

    if target_host.port:
        cmd += ["--ssh-port", str(target_host.port)]

    key_pair = create_secret_key_nixos_anywhere()
    cmd += ["-i", str(key_pair.private)]

    backup_file = None
    if hw_file.exists():
        backup_file = hw_file.with_suffix(".bak")
        hw_file.replace(backup_file)

    cmd += [target_host.target]
    cmd = nix_shell(
        ["nixos-anywhere"],
        cmd,
    )

    run(
        cmd,
        RunOpts(log=Log.BOTH, prefix=machine.name, needs_user_terminal=True),
    )
    print(f"Successfully generated: {hw_file}")

    # try to evaluate the machine
    # If it fails, the hardware-configuration.nix file is invalid
    commit_file(
        hw_file,
        opts.machine.flake.path,
        f"machines/{opts.machine.name}/{hw_file.name}: update hardware configuration",
    )
    try:
        get_machine_target_platform(opts.machine)
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


def get_machine_hardware_config(machine: Machine) -> HardwareConfig:
    """Detect and return the full hardware configuration for the given machine.

    Returns:
        HardwareConfig: Structured hardware information, or None if unavailable.

    """
    return HardwareConfig.detect_type(machine)


class MachineHardwareBrief(TypedDict):
    hardware_config: HardwareConfig
    platform: str | None


@API.register
def get_machine_hardware_summary(machine: Machine) -> MachineHardwareBrief:
    """Return a high-level summary of hardware config and platform type."""
    return {
        "hardware_config": get_machine_hardware_config(machine),
        "platform": get_machine_target_platform(machine),
    }
