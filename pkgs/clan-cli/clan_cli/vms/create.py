import argparse
import asyncio
import json
import os
import shlex
import sys
import tempfile
from pathlib import Path
from typing import Iterator
from uuid import UUID

from ..nix import nix_build, nix_config, nix_eval, nix_shell
from ..task_manager import BaseTask, Command, create_task
from .inspect import VmConfig, inspect_vm


class BuildVmTask(BaseTask):
    def __init__(self, uuid: UUID, vm: VmConfig, nix_options: list[str] = []) -> None:
        super().__init__(uuid, num_cmds=7)
        self.vm = vm
        self.nix_options = nix_options

    def get_vm_create_info(self, cmds: Iterator[Command]) -> dict:
        config = nix_config()
        system = config["system"]

        clan_dir = self.vm.flake_url
        machine = self.vm.flake_attr
        cmd = next(cmds)
        cmd.run(
            nix_build(
                [
                    f'{clan_dir}#clanInternals.machines."{system}"."{machine}".config.system.clan.vm.create'
                ]
                + self.nix_options
            ),
            name="buildvm",
        )
        vm_json = "".join(cmd.stdout).strip()
        self.log.debug(f"VM JSON path: {vm_json}")
        with open(vm_json) as f:
            return json.load(f)

    def get_clan_name(self, cmds: Iterator[Command]) -> str:
        clan_dir = self.vm.flake_url
        cmd = next(cmds)
        cmd.run(
            nix_eval([f"{clan_dir}#clanInternals.clanName"]) + self.nix_options,
            name="clanname",
        )
        clan_name = cmd.stdout[0].strip().strip('"')
        return clan_name

    def run(self) -> None:
        cmds = self.commands()

        machine = self.vm.flake_attr
        self.log.debug(f"Creating VM for {machine}")

        # TODO: We should get this from the vm argument
        vm_config = self.get_vm_create_info(cmds)
        clan_name = self.get_clan_name(cmds)

        self.log.debug(f"Building VM for clan name: {clan_name}")

        flake_dir = Path(self.vm.flake_url)
        flake_dir.mkdir(exist_ok=True)

        with tempfile.TemporaryDirectory() as tmpdir_:
            tmpdir = Path(tmpdir_)
            xchg_dir = tmpdir / "xchg"
            xchg_dir.mkdir(exist_ok=True)
            secrets_dir = tmpdir / "secrets"
            secrets_dir.mkdir(exist_ok=True)
            disk_img = tmpdir / "disk.img"

            env = os.environ.copy()
            env["CLAN_DIR"] = str(self.vm.flake_url)

            env["PYTHONPATH"] = str(
                ":".join(sys.path)
            )  # TODO do this in the clanCore module
            env["SECRETS_DIR"] = str(secrets_dir)

            # Only generate secrets for local clans
            if isinstance(self.vm.flake_url, Path) and self.vm.flake_url.is_dir():
                cmd = next(cmds)
                if Path(self.vm.flake_url).is_dir():
                    cmd.run(
                        [vm_config["generateSecrets"], clan_name],
                        env=env,
                        name="generateSecrets",
                    )
                else:
                    self.log.warning("won't generate secrets for non local clan")

            cmd = next(cmds)
            cmd.run(
                [vm_config["uploadSecrets"]],
                env=env,
                name="uploadSecrets",
            )

            cmd = next(cmds)
            cmd.run(
                nix_shell(
                    ["qemu"],
                    [
                        "qemu-img",
                        "create",
                        "-f",
                        "raw",
                        str(disk_img),
                        "1024M",
                    ],
                ),
                name="createDisk",
            )

            cmd = next(cmds)
            cmd.run(
                nix_shell(
                    ["e2fsprogs"],
                    [
                        "mkfs.ext4",
                        "-L",
                        "nixos",
                        str(disk_img),
                    ],
                ),
                name="formatDisk",
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
                "qemu-kvm",
                "-name",
                machine,
                "-m",
                f'{vm_config["memorySize"]}M',
                "-smp",
                str(vm_config["cores"]),
                "-cpu",
                "max",
                "-device",
                "virtio-rng-pci",
                "-net",
                "nic,netdev=user.0,model=virtio",
                "-netdev",
                "user,id=user.0",
                "-virtfs",
                "local,path=/nix/store,security_model=none,mount_tag=nix-store",
                "-virtfs",
                f"local,path={xchg_dir},security_model=none,mount_tag=shared",
                "-virtfs",
                f"local,path={xchg_dir},security_model=none,mount_tag=xchg",
                "-virtfs",
                f"local,path={secrets_dir},security_model=none,mount_tag=secrets",
                "-drive",
                f"cache=writeback,file={disk_img},format=raw,id=drive1,if=none,index=1,werror=report",
                "-device",
                "virtio-blk-pci,bootindex=1,drive=drive1,serial=root",
                "-device",
                "virtio-keyboard",
                # TODO: audio card
                # "-audiodev", "spice,id=audio0",
                # "-device", "intel-hda",
                # "-device", "hda-duplex,audiodev=audio0",
                # TODO: we also need to fixup timezone than...
                # "-rtc", "base=localtime,clock=host,driftfix=slew",
                "-vga",
                "virtio",
                "-usb",
                "-device",
                "usb-tablet,bus=usb-bus.0",
                "-kernel",
                f'{vm_config["toplevel"]}/kernel',
                "-initrd",
                vm_config["initrd"],
                "-append",
                " ".join(cmdline),
            ]
            if not self.vm.graphics:
                qemu_command.append("-nographic")
            print("$ " + shlex.join(qemu_command))
            cmd.run(nix_shell(["qemu"], qemu_command), name="qemu")


def create_vm(vm: VmConfig, nix_options: list[str] = []) -> BuildVmTask:
    return create_task(BuildVmTask, vm, nix_options)


def create_command(args: argparse.Namespace) -> None:
    flake_url = args.flake_url or args.flake
    vm = asyncio.run(inspect_vm(flake_url=flake_url, flake_attr=args.machine))

    task = create_vm(vm, args.option)
    for line in task.log_lines():
        print(line, end="")


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str, help="machine in the flake to create")
    parser.add_argument("--flake_url", type=str, help="flake url")
    parser.set_defaults(func=create_command)
