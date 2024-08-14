import argparse
import dataclasses
import json
import logging
from pathlib import Path

from clan_cli.api import API
from clan_cli.errors import ClanError

from ..cmd import run, run_no_stdout
from ..completions import add_dynamic_completer, complete_machines
from ..nix import nix_config, nix_eval, nix_shell
from .types import machine_name_type

log = logging.getLogger(__name__)


@dataclasses.dataclass
class HardwareInfo:
    system: str | None


@API.register
def show_machine_hardware_info(
    clan_dir: str | Path, machine_name: str
) -> HardwareInfo | None:
    """
    Show hardware information for a machine returns None if none exist.
    """

    hw_file = Path(f"{clan_dir}/machines/{machine_name}/hardware-configuration.nix")

    is_template = hw_file.exists() and "throw" in hw_file.read_text()
    if not hw_file.exists() or is_template:
        return None

    system = show_machine_hardware_platform(clan_dir, machine_name)
    return HardwareInfo(system)


@API.register
def show_machine_deployment_target(
    clan_dir: str | Path, machine_name: str
) -> str | None:
    """
    Show hardware information for a machine returns None if none exist.
    """
    config = nix_config()
    system = config["system"]
    cmd = nix_eval(
        [
            f"{clan_dir}#clanInternals.machines.{system}.{machine_name}",
            "--apply",
            "machine: { inherit (machine.config.clan.core.networking) targetHost; }",
            "--json",
        ]
    )
    proc = run_no_stdout(cmd)
    res = proc.stdout.strip()

    target_host = json.loads(res)
    return target_host.get("targetHost", None)


@API.register
def show_machine_hardware_platform(
    clan_dir: str | Path, machine_name: str
) -> str | None:
    """
    Show hardware information for a machine returns None if none exist.
    """
    config = nix_config()
    system = config["system"]
    cmd = nix_eval(
        [
            f"{clan_dir}#clanInternals.machines.{system}.{machine_name}",
            "--apply",
            "machine: { inherit (machine.config.nixpkgs.hostPlatform) system; }",
            "--json",
        ]
    )
    proc = run_no_stdout(cmd)
    res = proc.stdout.strip()

    host_platform = json.loads(res)
    return host_platform.get("system", None)


@API.register
def generate_machine_hardware_info(
    clan_dir: str | Path,
    machine_name: str,
    hostname: str,
    password: str | None = None,
    keyfile: str | None = None,
    force: bool | None = False,
) -> HardwareInfo:
    """
    Generate hardware information for a machine
    and place the resulting *.nix file in the machine's directory.
    """
    cmd = nix_shell(
        [
            "nixpkgs#openssh",
            "nixpkgs#sshpass",
            # Provides nixos-generate-config on non-NixOS systems
            "nixpkgs#nixos-install-tools",
        ],
        [
            *(["sshpass", "-p", f"{password}"] if password else []),
            "ssh",
            *(["-i", f"{keyfile}"] if keyfile else []),
            # Disable strict host key checking
            "-o StrictHostKeyChecking=no",
            # Disable known hosts file
            "-o UserKnownHostsFile=/dev/null",
            f"{hostname}",
            "nixos-generate-config",
            # Filesystems are managed by disko
            "--no-filesystems",
            "--show-hardware-config",
        ],
    )
    out = run(cmd)
    if out.returncode != 0:
        log.error(f"Failed to inspect {machine_name}. Address: {hostname}")
        log.error(out)
        raise ClanError(f"Failed to inspect {machine_name}. Address: {hostname}")

    hw_file = Path(f"{clan_dir}/machines/{machine_name}/hardware-configuration.nix")
    hw_file.parent.mkdir(parents=True, exist_ok=True)

    # Check if the hardware-configuration.nix file is a template
    is_template = hw_file.exists() and "throw" in hw_file.read_text()

    if hw_file.exists() and not force and not is_template:
        raise ClanError(
            "File exists.",
            description="Hardware file already exists. To force overwrite the existing configuration use '--force'.",
            location=f"{__name__} {hw_file}",
        )

    with open(hw_file, "w") as f:
        f.write(out.stdout)
        print(f"Successfully generated: {hw_file}")

    system = show_machine_hardware_platform(clan_dir, machine_name)
    return HardwareInfo(system)


def hw_generate_command(args: argparse.Namespace) -> None:
    flake_path = args.flake.path
    hw_info = generate_machine_hardware_info(
        flake_path, args.machine, args.hostname, args.password, args.force
    )
    print("----")
    print("Successfully generated hardware information.")
    print(f"Target: {args.machine} ({args.hostname})")
    print(f"System: {hw_info.system}")
    print("----")


def register_hw_generate(parser: argparse.ArgumentParser) -> None:
    parser.set_defaults(func=hw_generate_command)
    machine_parser = parser.add_argument(
        "machine",
        help="the name of the machine",
        type=machine_name_type,
    )
    machine_parser = parser.add_argument(
        "hostname",
        help="hostname of the machine",
        type=str,
    )
    machine_parser = parser.add_argument(
        "--password",
        help="Pre-provided password the cli will prompt otherwise if needed.",
        type=str,
        required=False,
    )
    machine_parser = parser.add_argument(
        "--force",
        help="Will overwrite the hardware-configuration.nix file.",
        action="store_true",
    )
    add_dynamic_completer(machine_parser, complete_machines)
