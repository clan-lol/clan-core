import asyncio
import json
import shlex
from typing import Annotated, AsyncIterator

from fastapi import APIRouter, Body, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse

from ...nix import nix_build, nix_eval
from ..schemas import VmConfig, VmInspectResponse

router = APIRouter()


class NixBuildException(HTTPException):
    def __init__(self, msg: str, loc: list = ["body", "flake_attr"]):
        detail = [
            {
                "loc": loc,
                "msg": msg,
                "type": "value_error",
            }
        ]
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )


def nix_build_exception_handler(
    request: Request, exc: NixBuildException
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(dict(detail=exc.detail)),
    )


def nix_inspect_vm(machine: str, flake_url: str) -> list[str]:
    return nix_eval(
        [
            f"{flake_url}#nixosConfigurations.{json.dumps(machine)}.config.system.clan.vm.config"
        ]
    )


def nix_build_vm(machine: str, flake_url: str) -> list[str]:
    return nix_build(
        [
            f"{flake_url}#nixosConfigurations.{json.dumps(machine)}.config.system.build.vm"
        ]
    )


@router.post("/api/vms/inspect")
async def inspect_vm(
    flake_url: Annotated[str, Body()], flake_attr: Annotated[str, Body()]
) -> VmInspectResponse:
    cmd = nix_inspect_vm(flake_attr, flake_url=flake_url)
    proc = await asyncio.create_subprocess_exec(
        cmd[0],
        *cmd[1:],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        raise NixBuildException(
            f"""
Failed to evaluate vm from '{flake_url}#{flake_attr}'.
command: {shlex.join(cmd)}
exit code: {proc.returncode}
command output:
{stderr.decode("utf-8")}
"""
        )
    data = json.loads(stdout)
    return VmInspectResponse(
        config=VmConfig(flake_url=flake_url, flake_attr=flake_attr, **data)
    )


async def vm_build(vm: VmConfig) -> AsyncIterator[str]:
    cmd = nix_build_vm(vm.flake_attr, flake_url=vm.flake_url)
    proc = await asyncio.create_subprocess_exec(
        cmd[0],
        *cmd[1:],
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    assert proc.stdout is not None and proc.stderr is not None
    async for line in proc.stdout:
        yield line.decode("utf-8", "ignore")
    stderr = ""
    async for line in proc.stderr:
        stderr += line.decode("utf-8", "ignore")
    res = await proc.wait()
    if res != 0:
        raise NixBuildException(
            f"""
Failed to build vm from '{vm.flake_url}#{vm.flake_attr}'.
command: {shlex.join(cmd)}
exit code: {res}
command output:
{stderr}
            """
        )


@router.post("/api/vms/create")
async def create_vm(vm: Annotated[VmConfig, Body()]) -> StreamingResponse:
    return StreamingResponse(vm_build(vm))
