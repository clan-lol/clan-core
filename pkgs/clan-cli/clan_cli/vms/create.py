import argparse
import asyncio
import json
import shlex
import tempfile
from pathlib import Path
from typing import Iterator
from uuid import UUID

from ..dirs import get_clan_flake_toplevel
from ..nix import nix_build, nix_shell
from ..task_manager import BaseTask, Command, create_task
from .inspect import VmConfig, inspect_vm


class BuildVmTask(BaseTask):
    def __init__(self, uuid: UUID, vm: VmConfig) -> None:
        super().__init__(uuid)
        self.vm = vm

    def get_vm_create_info(self, cmds: Iterator[Command]) -> dict:
        clan_dir = self.vm.flake_url
        machine = self.vm.flake_attr
        cmd = next(cmds)
        cmd.run(
            nix_build(
                [
                    # f'{clan_dir}#clanInternals.machines."{system}"."{machine}".config.clan.virtualisation.createJSON' # TODO use this
                    f'{clan_dir}#nixosConfigurations."{machine}".config.system.clan.vm.create'
                ]
            )
        )
        vm_json = "".join(cmd.lines)
        self.log.debug(f"VM JSON path: {vm_json}")
        with open(vm_json.strip()) as f:
            return json.load(f)

    def run(self) -> None:
        cmds = self.register_commands(4)

        machine = self.vm.flake_attr
        self.log.debug(f"Creating VM for {machine}")

        # TODO: We should get this from the vm argument
        vm_config = self.get_vm_create_info(cmds)

        with tempfile.TemporaryDirectory() as tmpdir_:
            xchg_dir = Path(tmpdir_) / "xchg"
            xchg_dir.mkdir()
            disk_img = f"{tmpdir_}/disk.img"

            cmd = next(cmds)
            cmd.run(
                nix_shell(
                    ["qemu"],
                    [
                        "qemu-img",
                        "create",
                        "-f",
                        "raw",
                        disk_img,
                        "1024M",
                    ],
                )
            )

            cmd = next(cmds)
            cmd.run(
                nix_shell(
                    ["e2fsprogs"],
                    [
                        "mkfs.ext4",
                        "-L",
                        "nixos",
                        disk_img,
                    ],
                )
            )

            cmd = next(cmds)
            cmdline = [
                (Path(vm_config["toplevel"]) / "kernel-params").read_text(),
                f'init={vm_config["toplevel"]}/init',
                f'regInfo={vm_config["regInfo"]}/registration',
                "console=ttyS0,115200n8",
                "console=tty0",
            ]
            qemu_command = [
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
                "-append", " ".join(cmdline),
                # fmt: on
            ]
            if not self.vm.graphics:
                qemu_command.append("-nographic")
            print("$ " + shlex.join(qemu_command))
            cmd.run(nix_shell(["qemu"], qemu_command))


def create_vm(vm: VmConfig) -> BuildVmTask:
    return create_task(BuildVmTask, vm)


def create_command(args: argparse.Namespace) -> None:
    clan_dir = get_clan_flake_toplevel().as_posix()
    vm = asyncio.run(inspect_vm(flake_url=clan_dir, flake_attr=args.machine))

    task = create_vm(vm)
    for line in task.log_lines():
        print(line, end="")


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str)
    parser.set_defaults(func=create_command)
