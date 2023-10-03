import argparse
import asyncio

from ..dirs import get_clan_flake_toplevel
from ..webui.routers import vms


def inspect(args: argparse.Namespace) -> None:
    clan_dir = get_clan_flake_toplevel().as_posix()
    res = asyncio.run(vms.inspect_vm(flake_url=clan_dir, flake_attr=args.machine))
    print(res.json())


def register_inspect_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str)
    parser.set_defaults(func=inspect)
