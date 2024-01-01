import argparse
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ..dirs import specific_groot_dir
from ..errors import ClanError
from ..machines.list import list_machines
from ..nix import nix_build, nix_config, nix_eval, nix_metadata
from ..vms.inspect import VmConfig, inspect_vm


@dataclass
class FlakeConfig:
    flake_url: str | Path
    flake_attr: str

    clan_name: str
    nar_hash: str
    icon: str | None
    description: str | None
    last_updated: str
    revision: str | None
    vm: VmConfig


def run_cmd(cmd: list[str]) -> str:
    proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE)
    assert proc.stdout is not None
    if proc.returncode != 0:
        raise ClanError(
            f"""
command: {shlex.join(cmd)}
exit code: {proc.returncode}
stdout:
{proc.stdout}
"""
        )

    return proc.stdout.strip()


def inspect_flake(flake_url: str | Path, flake_attr: str) -> FlakeConfig:
    config = nix_config()
    system = config["system"]

    # Check if the machine exists
    machines = list_machines(flake_url)
    if flake_attr not in machines:
        raise ClanError(
            f"Machine {flake_attr} not found in {flake_url}. Available machines: {', '.join(machines)}"
        )

    vm = inspect_vm(flake_url, flake_attr)

    # Get the cLAN name
    cmd = nix_eval(
        [
            f'{flake_url}#clanInternals.machines."{system}"."{flake_attr}".config.clanCore.clanName'
        ]
    )
    res = run_cmd(cmd)
    clan_name = res.strip('"')

    # Get the clan icon path
    cmd = nix_eval(
        [
            f'{flake_url}#clanInternals.machines."{system}"."{flake_attr}".config.clanCore.clanIcon'
        ]
    )
    res = run_cmd(cmd)

    # If the icon is null, no icon is set for this cLAN
    if res == "null":
        icon_path = None
    else:
        icon_path = res.strip('"')

        cmd = nix_build(
            [
                f'{flake_url}#clanInternals.machines."{system}"."{flake_attr}".config.clanCore.clanIcon'
            ],
            specific_groot_dir(clan_name=clan_name, flake_url=str(flake_url))
            / "clanIcon",
        )
        run_cmd(cmd)

    # Get the flake metadata
    meta = nix_metadata(flake_url)

    return FlakeConfig(
        vm=vm,
        flake_url=flake_url,
        clan_name=clan_name,
        flake_attr=flake_attr,
        nar_hash=meta["locked"]["narHash"],
        icon=icon_path,
        description=meta.get("description"),
        last_updated=meta["lastModified"],
        revision=meta.get("revision"),
    )


@dataclass
class InspectOptions:
    machine: str
    flake: Path


def inspect_command(args: argparse.Namespace) -> None:
    inspect_options = InspectOptions(
        machine=args.machine,
        flake=args.flake or Path.cwd(),
    )
    res = inspect_flake(
        flake_url=inspect_options.flake, flake_attr=inspect_options.machine
    )
    print("cLAN name:", res.clan_name)
    print("Icon:", res.icon)
    print("Description:", res.description)
    print("Last updated:", res.last_updated)
    print("Revision:", res.revision)


def register_inspect_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--machine", type=str, default="defaultVM")
    parser.set_defaults(func=inspect_command)
