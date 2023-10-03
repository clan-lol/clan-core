import argparse
import asyncio
from typing import Any, Iterator
from uuid import UUID

from fastapi.responses import StreamingResponse

from ..dirs import get_clan_flake_toplevel
from ..webui.routers import vms
from ..webui.schemas import VmConfig


def read_stream_response(stream: StreamingResponse) -> Iterator[Any]:
    iterator = stream.body_iterator
    while True:
        try:
            tem = asyncio.run(iterator.__anext__())  # type: ignore
        except StopAsyncIteration:
            break
        yield tem


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
    uuid = UUID(res.uuid)

    stream = asyncio.run(vms.get_vm_logs(uuid))

    for line in read_stream_response(stream):
        print(line)


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str)
    parser.set_defaults(func=create)
