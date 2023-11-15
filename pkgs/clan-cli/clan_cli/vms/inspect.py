import argparse
import asyncio
import json
from pathlib import Path

from pydantic import AnyUrl, BaseModel

from ..async_cmd import run
from ..dirs import specific_flake_dir
from ..nix import nix_config, nix_eval


class VmConfig(BaseModel):
    flake_url: AnyUrl | Path
    flake_attr: str

    cores: int
    memory_size: int
    graphics: bool


async def inspect_vm(flake_url: AnyUrl | Path, flake_attr: str) -> VmConfig:
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
    clan_dir = specific_flake_dir(args.flake)
    res = asyncio.run(inspect_vm(flake_url=clan_dir, flake_attr=args.machine))
    print("Cores:", res.cores)
    print("Memory size:", res.memory_size)
    print("Graphics:", res.graphics)


def register_inspect_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str)
    parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to create machine for",
    )
    parser.set_defaults(func=inspect_command)