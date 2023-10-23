import argparse
import asyncio
import json
import os
import shlex
import sys
import re
from pathlib import Path
from typing import Iterator, Dict
from uuid import UUID

from ..dirs import clan_flakes_dir, specific_flake_dir
from ..nix import nix_build, nix_config, nix_eval, nix_shell
from ..task_manager import BaseTask, Command, create_task
from ..types import validate_path
from .inspect import VmConfig, inspect_vm
from ..errors import ClanError
from ..debug import repro_env_break


def is_path_or_url(s: str) -> str | None:
    # check if s is a valid path
    if os.path.exists(s):
        return "path"
    # check if s is a valid URL
    elif re.match(r"^https?://[a-zA-Z0-9.-]+/[a-zA-Z0-9.-]+", s):
        return "URL"
    # otherwise, return None
    else:
        return None

class BuildVmTask(BaseTask):
    def __init__(self, uuid: UUID, vm: VmConfig) -> None:
        super().__init__(uuid, num_cmds=7)
        self.vm = vm

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
            )
        )
        vm_json = "".join(cmd.stdout).strip()
        self.log.debug(f"VM JSON path: {vm_json}")
        with open(vm_json) as f:
            return json.load(f)

    def get_clan_name(self, cmds: Iterator[Command]) -> str:
        clan_dir = self.vm.flake_url
        cmd = next(cmds)
        cmd.run(nix_eval([f"{clan_dir}#clanInternals.clanName"]))
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

        flake_dir = clan_flakes_dir() / clan_name
        validate_path(clan_flakes_dir(), flake_dir)
        flake_dir.mkdir(exist_ok=True)

        xchg_dir = flake_dir / "xchg"
        xchg_dir.mkdir()
        secrets_dir = flake_dir / "secrets"
        secrets_dir.mkdir()
        disk_img = f"{flake_dir}/disk.img"

        env = os.environ.copy()
        env["CLAN_DIR"] = str(self.vm.flake_url)

        env["PYTHONPATH"] = str(
            ":".join(sys.path)
        )  # TODO do this in the clanCore module
        env["SECRETS_DIR"] = str(secrets_dir)

        res = is_path_or_url(str(self.vm.flake_url))
        if res is None:
            raise ClanError(
                f"flake_url must be a valid path or URL, got {self.vm.flake_url}"
            )
        elif res == "path": # Only generate secrets for local clans
            cmd = next(cmds)
            if Path(self.vm.flake_url).is_dir():
                cmd.run(
                    [vm_config["generateSecrets"], clan_name],
                    env=env,
                )
            else:
                self.log.warning("won't generate secrets for non local clan")


        cmd = next(cmds)
        cmd.run(
            [vm_config["uploadSecrets"], clan_name],
            env=env,
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
            "-virtfs", f"local,path={secrets_dir},security_model=none,mount_tag=secrets",
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
    clan_dir = specific_flake_dir(args.flake)
    vm = asyncio.run(inspect_vm(flake_url=clan_dir, flake_attr=args.machine))

    task = create_vm(vm)
    for line in task.log_lines():
        print(line, end="")


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str)
    parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to create machine for",
    )
    parser.set_defaults(func=create_command)
