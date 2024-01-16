import argparse
import json
from dataclasses import dataclass
from pathlib import Path

from ..cmd import run
from ..nix import nix_config, nix_eval


@dataclass
class VmConfig:
    clan_name: str
    flake_url: str | Path
    flake_attr: str

    cores: int
    memory_size: int
    graphics: bool
    wayland: bool = False


def inspect_vm(flake_url: str | Path, flake_attr: str) -> VmConfig:
    config = nix_config()
    system = config["system"]

    cmd = nix_eval(
        [
            f'{flake_url}#clanInternals.machines."{system}"."{flake_attr}".config.clanCore.vm.inspect',
            "--refresh",
        ]
    )

    proc = run(cmd)

    data = json.loads(proc.stdout)
    return VmConfig(flake_url=flake_url, flake_attr=flake_attr, **data)


@dataclass
class InspectOptions:
    machine: str
    flake: Path


def inspect_command(args: argparse.Namespace) -> None:
    inspect_options = InspectOptions(
        machine=args.machine,
        flake=args.flake or Path.cwd(),
    )
    res = inspect_vm(
        flake_url=inspect_options.flake, flake_attr=inspect_options.machine
    )
    print("Cores:", res.cores)
    print("Memory size:", res.memory_size)
    print("Graphics:", res.graphics)


def register_inspect_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str, default="defaultVM")
    parser.set_defaults(func=inspect_command)
