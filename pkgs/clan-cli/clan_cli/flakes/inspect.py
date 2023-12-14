import argparse
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ..errors import ClanError
from ..machines.list import list_machines
from ..nix import nix_build, nix_config, nix_eval, nix_metadata


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


def inspect_flake(flake_url: str | Path, flake_attr: str) -> FlakeConfig:
    config = nix_config()
    system = config["system"]

    machines = list_machines(flake_url)
    if flake_attr not in machines:
        raise ClanError(
            f"Machine {flake_attr} not found in {flake_url}. Available machines: {', '.join(machines)}"
        )

    cmd = nix_eval(
        [
            f'{flake_url}#clanInternals.machines."{system}"."{flake_attr}".config.clanCore.clanIcon'
        ]
    )

    proc = subprocess.run(cmd, text=True, capture_output=True)
    assert proc.stdout is not None
    if proc.returncode != 0:
        raise ClanError(
            f"""
command: {shlex.join(cmd)}
exit code: {proc.returncode}
stdout:
{proc.stdout}
stderr:
{proc.stderr}
"""
        )
    res = proc.stdout.strip()
    if res == "null":
        icon_path = None
    else:
        icon_path = res.strip('"')

        if not Path(icon_path).exists():
            cmd = nix_build(
                [
                    f'{flake_url}#clanInternals.machines."{system}"."{flake_attr}".config.clanCore.clanIcon'
                ]
            )
            proc = subprocess.run(cmd, text=True, capture_output=True)
            assert proc.stdout is not None
            if proc.returncode != 0:
                raise ClanError(
                    f"""
command: {shlex.join(cmd)}
exit code: {proc.returncode}
stdout:
{proc.stdout}
stderr:
{proc.stderr}
"""
                )

    cmd = nix_eval(
        [
            f'{flake_url}#clanInternals.machines."{system}"."{flake_attr}".config.clanCore.clanName'
        ]
    )

    proc = subprocess.run(cmd, text=True, capture_output=True)
    assert proc.stdout is not None
    if proc.returncode != 0:
        raise ClanError(
            f"""
command: {shlex.join(cmd)}
exit code: {proc.returncode}
stdout:
{proc.stdout}
stderr:
{proc.stderr}
"""
        )
    clan_name = proc.stdout.strip().strip('"')

    meta = nix_metadata(flake_url)

    return FlakeConfig(
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
