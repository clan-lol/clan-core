import argparse
import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

from ..async_cmd import run
from ..nix import nix_config, nix_eval


@dataclass
class VmConfig:
    flake_url: str | Path
    flake_attr: str

    cores: int
    memory_size: int
    graphics: bool


async def inspect_vm(flake_url: str | Path, flake_attr: str) -> VmConfig:
    config = nix_config()
    system = config["system"]

    cmd = nix_eval(
        [
            f'{flake_url}#clanInternals.machines."{system}"."{flake_attr}".config.system.clan.vm.config'
        ]
    )
    out = await run(cmd)
    data = json.loads(out.stdout)
    return VmConfig(flake_url=flake_url, flake_attr=flake_attr, **data)


def inspect_command(args: argparse.Namespace) -> None:
    clan_dir = Path(args.flake)
    res = asyncio.run(inspect_vm(flake_url=clan_dir, flake_attr=args.machine))
    print("Cores:", res.cores)
    print("Memory size:", res.memory_size)
    print("Graphics:", res.graphics)


def register_inspect_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str)
    parser.set_defaults(func=inspect_command)
