import asyncio
import json
import logging
import shlex
from typing import Annotated, Iterator
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Body, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse

from ...nix import nix_build, nix_eval
from ..schemas import VmConfig, VmCreateResponse, VmInspectResponse, VmStatusResponse
from ..task_manager import BaseTask, get_task, register_task

log = logging.getLogger(__name__)
router = APIRouter()


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


class BuildVmTask(BaseTask):
    def __init__(self, uuid: UUID, vm: VmConfig) -> None:
        super().__init__(uuid)
        self.vm = vm

    def run(self) -> None:
        try:
            self.log.debug(f"BuildVM with uuid {self.uuid} started")
            cmd = nix_build_vm_cmd(self.vm.flake_attr, flake_url=self.vm.flake_url)

            proc = self.run_cmd(cmd)
            self.log.debug(f"stdout: {proc.stdout}")

            vm_path = f"{''.join(proc.stdout[0])}/bin/run-nixos-vm"
            self.log.debug(f"vm_path: {vm_path}")

            self.run_cmd([vm_path])
            self.finished = True
        except Exception as e:
            self.failed = True
            self.finished = True
            log.exception(e)


def nix_build_exception_handler(
    request: Request, exc: NixBuildException
) -> JSONResponse:
    log.error("NixBuildException: %s", exc)
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(dict(detail=exc.detail)),
    )


##################################
#                                #
#  ======== VM ROUTES ========   #
#                                #
##################################
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


@router.get("/api/vms/{uuid}/status")
async def get_status(uuid: UUID) -> VmStatusResponse:
    task = get_task(uuid)
    return VmStatusResponse(running=not task.finished, status=0)


@router.get("/api/vms/{uuid}/logs")
async def get_logs(uuid: UUID) -> StreamingResponse:
    # Generator function that yields log lines as they are available
    def stream_logs() -> Iterator[str]:
        task = get_task(uuid)

        for proc in task.procs:
            if proc.done:
                log.debug("stream logs and proc is done")
                for line in proc.stderr:
                    yield line + "\n"
                for line in proc.stdout:
                    yield line + "\n"
                continue
            while True:
                out = proc.output
                line = out.get()
                if line is None:
                    log.debug("stream logs and line is None")
                    break
                yield line

    return StreamingResponse(
        content=stream_logs(),
        media_type="text/plain",
    )


@router.post("/api/vms/create")
async def create_vm(
    vm: Annotated[VmConfig, Body()], background_tasks: BackgroundTasks
) -> VmCreateResponse:
    uuid = register_task(BuildVmTask, vm)
    return VmCreateResponse(uuid=str(uuid))
