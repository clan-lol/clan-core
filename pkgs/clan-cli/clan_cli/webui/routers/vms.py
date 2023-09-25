import asyncio
import json
import logging
import os
import select
import queue
import shlex
import subprocess
import threading
from typing import Annotated, AsyncIterator
from uuid import UUID, uuid4

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Body,
    HTTPException,
    Request,
    status,
)
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, StreamingResponse

from ...nix import nix_build, nix_eval
from ..schemas import VmConfig, VmCreateResponse, VmInspectResponse, VmStatusResponse

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
    def __init__(self, uuid: UUID, msg: str, loc: list = ["body", "flake_attr"]):
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


class ProcessState:
    def __init__(self, proc: subprocess.Popen):
        self.proc: subprocess.Process = proc
        self.stdout: list[str] = []
        self.stderr: list[str] = []
        self.returncode: int | None = None
        self.done: bool = False

class BuildVM(threading.Thread):
    def __init__(self, vm: VmConfig, uuid: UUID):
        # calling parent class constructor
        threading.Thread.__init__(self)

        # constructor
        self.vm: VmConfig = vm
        self.uuid: UUID = uuid
        self.log = logging.getLogger(__name__)
        self.procs: list[ProcessState] = []
        self.failed: bool = False
        self.finished: bool = False

    def run(self):
        try:

            self.log.debug(f"BuildVM with uuid {self.uuid} started")
            cmd = nix_build_vm_cmd(self.vm.flake_attr, flake_url=self.vm.flake_url)

            proc = self.run_cmd(cmd)
            out = proc.stdout
            self.log.debug(f"out: {out}")

            vm_path = f"{''.join(out)}/bin/run-nixos-vm"
            self.log.debug(f"vm_path: {vm_path}")
            self.run_cmd(vm_path)

            self.finished = True
        except Exception as e:
            self.failed = True
            self.finished = True
            log.exception(e)

    def run_cmd(self, cmd: list[str]) -> ProcessState:
        cwd = os.getcwd()
        log.debug(f"Working directory: {cwd}")
        log.debug(f"Running command: {shlex.join(cmd)}")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            cwd=cwd,
        )
        state = ProcessState(process)
        self.procs.append(state)

        while process.poll() is None:
            # Check if stderr is ready to be read from
            rlist, _, _ = select.select([process.stderr, process.stdout], [], [], 0)
            if process.stderr in rlist:
                line = process.stderr.readline()
                state.stderr.append(line)
            if process.stdout in rlist:
                line = process.stdout.readline()
                state.stdout.append(line)

        state.returncode = process.returncode
        state.done = True

        if process.returncode != 0:
            raise NixBuildException(
                self.uuid, f"Failed to run command: {shlex.join(cmd)}"
            )

        log.debug("Successfully ran command")
        return state


class VmTaskPool:
    def __init__(self) -> None:
        self.lock: threading.RLock = threading.RLock()
        self.pool: dict[UUID, BuildVM] = {}

    def __getitem__(self, uuid: str | UUID) -> BuildVM:
        with self.lock:
            if type(uuid) is UUID:
                return self.pool[uuid]
            else:
                uuid = UUID(uuid)
                return self.pool[uuid]

    def __setitem__(self, uuid: UUID, vm: BuildVM) -> None:
        with self.lock:
            if uuid in self.pool:
                raise KeyError(f"VM with uuid {uuid} already exists")
            if type(uuid) is not UUID:
                raise TypeError("uuid must be of type UUID")
            self.pool[uuid] = vm


POOL: VmTaskPool = VmTaskPool()


def nix_build_exception_handler(
    request: Request, exc: NixBuildException
) -> JSONResponse:
    log.error("NixBuildException: %s", exc)
    # del POOL[exc.uuid]
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(dict(detail=exc.detail)),
    )


@router.get("/api/vms/{uuid}/status")
async def get_status(uuid: str) -> VmStatusResponse:
    global POOL
    handle = POOL[uuid]

    if handle.process.poll() is None:
        return VmStatusResponse(running=True, status=0)
    else:
        return VmStatusResponse(running=False, status=handle.process.returncode)



@router.get("/api/vms/{uuid}/logs")
async def get_logs(uuid: str) -> StreamingResponse:
    async def stream_logs() -> AsyncIterator[str]:
        global POOL
        handle = POOL[uuid]
        for proc in handle.procs.values():
            while True:
                if proc.stdout.empty() and proc.stderr.empty() and not proc.done:
                    await asyncio.sleep(0.1)
                    continue
                if proc.stdout.empty() and proc.stderr.empty() and proc.done:
                    break
                for line in proc.stdout:
                    yield line
                for line in proc.stderr:
                    yield line

    return StreamingResponse(
        content=stream_logs(),
        media_type="text/plain",
    )


@router.post("/api/vms/create")
async def create_vm(
    vm: Annotated[VmConfig, Body()], background_tasks: BackgroundTasks
) -> VmCreateResponse:
    global POOL
    uuid = uuid4()
    handle = BuildVM(vm, uuid)
    handle.start()
    POOL[uuid] = handle
    return VmCreateResponse(uuid=str(uuid))
