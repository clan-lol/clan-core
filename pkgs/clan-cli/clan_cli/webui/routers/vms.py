import asyncio
import json
import logging
import os
import shlex
import uuid
from typing import Annotated, AsyncIterator

from fastapi import APIRouter, Body, FastAPI, HTTPException, Request, status, BackgroundTasks
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse

from ...nix import nix_build, nix_eval
from ..schemas import VmConfig, VmInspectResponse, VmCreateResponse

# Logging setup
log = logging.getLogger(__name__)

router = APIRouter()
app = FastAPI()



def nix_inspect_vm_cmd(machine: str, flake_url: str) -> list[str]:
    return nix_eval(
        [
            f"{flake_url}#nixosConfigurations.{json.dumps(machine)}.config.system.clan.vm.config"
        ]
    )


def nix_build_vm_cmd(machine: str, flake_url: str) -> list[str]:
    return nix_build(
        [
            f"{flake_url}#nixosConfigurations.{json.dumps(machine)}.config.system.build.vm"
        ]
    )




@router.post("/api/vms/inspect")
async def inspect_vm(
    flake_url: Annotated[str, Body()], flake_attr: Annotated[str, Body()]
) -> VmInspectResponse:
    cmd = nix_inspect_vm_cmd(flake_attr, flake_url=flake_url)
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



class NixBuildException(HTTPException):
    def __init__(self, uuid: uuid.UUID, msg: str,loc: list = ["body", "flake_attr"]):
        self.uuid = uuid
        detail = [
            {
                "loc": loc,
                "uuid": str(uuid),
                "msg": msg,
                "type": "value_error",
            }
        ]
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail
        )



import threading
import subprocess
import uuid


class BuildVM(threading.Thread):
    def __init__(self, vm: VmConfig, uuid: uuid.UUID):
        # calling parent class constructor
        threading.Thread.__init__(self)

        # constructor
        self.vm: VmConfig = vm
        self.uuid: uuid.UUID = uuid
        self.log = logging.getLogger(__name__)
        self.process: subprocess.Popen = None

    def run(self):
        self.log.debug(f"BuildVM with uuid {self.uuid} started")

        cmd = nix_build_vm_cmd(self.vm.flake_attr, flake_url=self.vm.flake_url)
        (out, err) = self.run_cmd(cmd)
        vm_path = f'{out.strip()}/bin/run-nixos-vm'

        self.log.debug(f"vm_path: {vm_path}")

        (out, err) = self.run_cmd(vm_path)


    def run_cmd(self, cmd: list[str]):
        cwd=os.getcwd()
        log.debug(f"Working directory: {cwd}")
        log.debug(f"Running command: {shlex.join(cmd)}")
        self.process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            cwd=cwd,
        )

        self.process.wait()
        if self.process.returncode != 0:
            raise NixBuildException(self.uuid, f"Failed to run command: {shlex.join(cmd)}")

        log.info("Successfully ran command")
        return (self.process.stdout, self.process.stderr)

POOL: dict[uuid.UUID, BuildVM] = {}


def nix_build_exception_handler(
    request: Request, exc: NixBuildException
) -> JSONResponse:
    log.error("NixBuildException: %s", exc)
    del POOL[exc.uuid]
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(dict(detail=exc.detail)),
    )


@router.post("/api/vms/create")
async def create_vm(vm: Annotated[VmConfig, Body()], background_tasks: BackgroundTasks) -> StreamingResponse:
    handle_id = uuid.uuid4()
    handle = BuildVM(vm, handle_id)
    handle.start()
    POOL[handle_id] = handle
    return VmCreateResponse(uuid=str(handle_id))


