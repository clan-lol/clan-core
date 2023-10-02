import argparse
import asyncio

from ..dirs import get_clan_flake_toplevel
from ..webui.routers import vms
from ..webui.schemas import VmConfig


def create(args: argparse.Namespace) -> None:
    clan_dir = get_clan_flake_toplevel().as_posix()
    vm = VmConfig(
        flake_url=clan_dir,
        flake_attr=args.machine,
        cores=0,
        graphics=False,
        memory_size=0,
    )

    res = asyncio.run(vms.create_vm(vm))
    print(res.json())


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str)
    parser.set_defaults(func=create)
