import json
import logging
import tempfile
from pathlib import Path
from typing import Annotated, Iterator
from uuid import UUID

from fastapi import APIRouter, Body
from fastapi import APIRouter, BackgroundTasks, Body, status
from fastapi.exceptions import HTTPException
from fastapi.responses import StreamingResponse

from ...nix import nix_build, nix_eval, nix_shell
from clan_cli.webui.routers.flake import get_attrs

from ...nix import nix_build, nix_eval
from ..schemas import VmConfig, VmCreateResponse, VmInspectResponse, VmStatusResponse
from ..task_manager import BaseTask, get_task, register_task
from .utils import run_cmd

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


class BuildVmTask(BaseTask):
    def __init__(self, uuid: UUID, vm: VmConfig) -> None:
        super().__init__(uuid)
        self.vm = vm

    def get_vm_create_info(self) -> dict:
        clan_dir = self.vm.flake_url
        machine = self.vm.flake_attr
        cmd_state = self.run_cmd(
            nix_build(
                [
                    # f'{clan_dir}#clanInternals.machines."{system}"."{machine}".config.clan.virtualisation.createJSON' # TODO use this
                    f'{clan_dir}#nixosConfigurations."{machine}".config.system.clan.vm.create'
                ]
            )
        )
        vm_json = "".join(cmd_state.stdout)
        self.log.debug(f"VM JSON path: {vm_json}")
        with open(vm_json) as f:
            return json.load(f)

    def task_run(self) -> None:
        machine = self.vm.flake_attr
        self.log.debug(f"Creating VM for {machine}")
        vm_config = self.get_vm_create_info()
        with tempfile.TemporaryDirectory() as tmpdir_:
            xchg_dir = Path(tmpdir_) / "xchg"
            xchg_dir.mkdir()
            disk_img = f"{tmpdir_}/disk.img"
            cmd = nix_shell(
                ["qemu"],
                [
                    "qemu" "qemu-img",
                    "create",
                    "-f",
                    "raw",
                    disk_img,
                    "1024M",
                ],
            )
            self.run_cmd(cmd)

            cmd = [
                "mkfs.ext4",
                "-L",
                "nixos",
                disk_img,
            ]
            self.run_cmd(cmd)

            cmd = nix_shell(
                ["qemu"],
                [
                    # fmt: off
                        "qemu-kvm",
                        "-name", machine,
                        "-m", f'{vm_config["memorySize"]}M',
                        "-smp", str(vm_config["cores"]),
                        "-device", "virtio-rng-pci",
                        "-net", "nic,netdev=user.0,model=virtio", "-netdev", "user,id=user.0",
                        "-virtfs", "local,path=/nix/store,security_model=none,mount_tag=nix-store",
                        "-virtfs", f"local,path={xchg_dir},security_model=none,mount_tag=shared",
                        "-virtfs", f"local,path={xchg_dir},security_model=none,mount_tag=xchg",
                        "-drive", f'cache=writeback,file={disk_img},format=raw,id=drive1,if=none,index=1,werror=report',
                        "-device", "virtio-blk-pci,bootindex=1,drive=drive1,serial=root",
                        "-device", "virtio-keyboard",
                        "-usb",
                        "-device", "usb-tablet,bus=usb-bus.0",
                        "-kernel", f'{vm_config["toplevel"]}/kernel',
                        "-initrd", vm_config["initrd"],
                        "-append", f'{(Path(vm_config["toplevel"]) / "kernel-params").read_text()} init={vm_config["toplevel"]}/init regInfo={vm_config["regInfo"]}/registration console=ttyS0,115200n8 console=tty0',
                    # fmt: on
                ],
            )
            self.run_cmd(cmd)

    # def run(self) -> None:
    #     try:
    #         self.log.debug(f"BuildVM with uuid {self.uuid} started")
    #         cmd = nix_build_vm_cmd(self.vm.flake_attr, flake_url=self.vm.flake_url)

    #         proc = self.run_cmd(cmd)
    #         self.log.debug(f"stdout: {proc.stdout}")

    #         vm_path = f"{''.join(proc.stdout[0])}/bin/run-nixos-vm"
    #         self.log.debug(f"vm_path: {vm_path}")

    #         self.run_cmd([vm_path])
    #         self.finished = True
    # except Exception as e:
    #     self.failed = True
    #     self.finished = True
    #     log.exception(e)


@router.post("/api/vms/inspect")
async def inspect_vm(
    flake_url: Annotated[str, Body()], flake_attr: Annotated[str, Body()]
) -> VmInspectResponse:
    cmd = nix_inspect_vm_cmd(flake_attr, flake_url=flake_url)
    stdout = await run_cmd(cmd)
    data = json.loads(stdout)
    return VmInspectResponse(
        config=VmConfig(flake_url=flake_url, flake_attr=flake_attr, **data)
    )


@router.get("/api/vms/{uuid}/status")
async def get_vm_status(uuid: UUID) -> VmStatusResponse:
    task = get_task(uuid)
    status: list[int | None] = list(map(lambda x: x.returncode, task.procs))
    log.debug(msg=f"returncodes: {status}. task.finished: {task.finished}")
    return VmStatusResponse(running=not task.finished, returncode=status)


@router.get("/api/vms/{uuid}/logs")
async def get_vm_logs(uuid: UUID) -> StreamingResponse:
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
    flake_attrs = await get_attrs(vm.flake_url)
    if vm.flake_attr not in flake_attrs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provided attribute '{vm.flake_attr}' does not exist.",
        )
    uuid = register_task(BuildVmTask, vm)
    return VmCreateResponse(uuid=str(uuid))
