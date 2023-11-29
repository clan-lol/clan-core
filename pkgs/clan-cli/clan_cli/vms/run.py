import argparse
import asyncio
import json
import os
import shlex
import subprocess
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path
from threading import Condition, Thread
from uuid import UUID

from ..nix import nix_build, nix_config, nix_eval, nix_shell
from ..task_manager import BaseTask, Command, create_task
from .inspect import VmConfig, inspect_vm


def qemu_command(
    vm: VmConfig,
    nixos_config: dict[str, str],
    xchg_dir: Path,
    secrets_dir: Path,
    disk_img: Path,
    spice_socket: Path,
) -> list[str]:
    kernel_cmdline = [
        (Path(nixos_config["toplevel"]) / "kernel-params").read_text(),
        f'init={nixos_config["toplevel"]}/init',
        f'regInfo={nixos_config["regInfo"]}/registration',
        "console=ttyS0,115200n8",
        "console=tty0",
    ]
    # fmt: off
    command = [
        "qemu-kvm",
        "-name", vm.flake_attr,
        "-m", f'{nixos_config["memorySize"]}M',
        "-smp", str(nixos_config["cores"]),
        "-cpu", "max",
        "-device", "virtio-rng-pci",
        "-net", "nic,netdev=user.0,model=virtio",
        "-netdev", "user,id=user.0",
        "-virtfs", "local,path=/nix/store,security_model=none,mount_tag=nix-store",
        "-virtfs", f"local,path={xchg_dir},security_model=none,mount_tag=shared",
        "-virtfs", f"local,path={xchg_dir},security_model=none,mount_tag=xchg",
        "-virtfs", f"local,path={secrets_dir},security_model=none,mount_tag=secrets",
        "-drive", f"cache=writeback,file={disk_img},format=raw,id=drive1,if=none,index=1,werror=report",
        "-device", "virtio-blk-pci,bootindex=1,drive=drive1,serial=root",
        "-device", "virtio-keyboard",
        # TODO: we also need to fixup timezone than...
        # "-rtc", "base=localtime,clock=host,driftfix=slew",
        "-vga", "virtio",
        "-usb", "-device", "usb-tablet,bus=usb-bus.0",
        "-kernel", f'{nixos_config["toplevel"]}/kernel',
        "-initrd", nixos_config["initrd"],
        "-append", " ".join(kernel_cmdline),
    ]  # fmt: on

    if vm.graphics:
        # fmt: off
        command.extend(
            [
                "-audiodev", "spice,id=audio0",
                "-device", "intel-hda",
                "-device", "hda-duplex,audiodev=audio0",
                "-device", "virtio-serial-pci",
                "-chardev", "spicevmc,id=vdagent0,name=vdagent",
                "-device", "virtserialport,chardev=vdagent0,name=com.redhat.spice.0",
                "-spice", f"unix=on,addr={spice_socket},disable-ticketing=on",
                "-device", "qemu-xhci,id=spicepass",
                "-chardev", "spicevmc,id=usbredirchardev1,name=usbredir",
                "-device", "usb-redir,chardev=usbredirchardev1,id=usbredirdev1",
                "-chardev", "spicevmc,id=usbredirchardev2,name=usbredir",
                "-device", "usb-redir,chardev=usbredirchardev2,id=usbredirdev2",
                "-chardev", "spicevmc,id=usbredirchardev3,name=usbredir",
                "-device", "usb-redir,chardev=usbredirchardev3,id=usbredirdev3",
                "-device", "pci-ohci,id=smartpass",
                "-device", "usb-ccid",
                "-chardev", "spicevmc,id=ccid,name=smartcard",
            ]
        )
        # fmt: on
    else:
        command.append("-nographic")
    return command


def start_spicy(spice_socket: Path, stop_condition: Condition) -> None:
    while not spice_socket.exists():
        with stop_condition:
            if stop_condition.wait(0.1):
                return

    spicy = nix_shell(["spice-gtk"], ["spicy", f"--uri=spice+unix://{spice_socket}"])
    proc = subprocess.Popen(spicy)
    while proc.poll() is None:
        with stop_condition:
            if stop_condition.wait(0.1):
                proc.terminate()
                proc.wait()


class BuildVmTask(BaseTask):
    def __init__(self, uuid: UUID, vm: VmConfig, nix_options: list[str] = []) -> None:
        super().__init__(uuid, num_cmds=7)
        self.vm = vm
        self.nix_options = nix_options

    def get_vm_create_info(self, cmds: Iterator[Command]) -> dict[str, str]:
        config = nix_config()
        system = config["system"]

        clan_dir = self.vm.flake_url
        machine = self.vm.flake_attr
        cmd = next(cmds)
        cmd.run(
            nix_build(
                [
                    f'{clan_dir}#clanInternals.machines."{system}"."{machine}".config.system.clan.vm.create',
                    *self.nix_options,
                ]
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
        nixos_config = self.get_vm_create_info(cmds)
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
            spice_socket = tmpdir / "spice.sock"

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
                        [nixos_config["generateSecrets"], clan_name],
                        env=env,
                        name="generateSecrets",
                    )
                else:
                    self.log.warning("won't generate secrets for non local clan")

            cmd = next(cmds)
            cmd.run(
                [nixos_config["uploadSecrets"]],
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

            qemu_cmd = qemu_command(
                self.vm,
                nixos_config,
                xchg_dir=xchg_dir,
                secrets_dir=secrets_dir,
                disk_img=disk_img,
                spice_socket=spice_socket,
            )
            stop_condition = Condition()
            spice_thread = Thread(
                target=start_spicy, args=(spice_socket, stop_condition), name="qemu"
            )
            spice_thread.start()

            print("$ " + shlex.join(qemu_cmd))
            try:
                cmd.run(nix_shell(["qemu"], qemu_cmd), name="qemu")
            finally:
                with stop_condition:
                    stop_condition.notify()
                spice_thread.join()


def run_vm(vm: VmConfig, nix_options: list[str] = []) -> BuildVmTask:
    return create_task(BuildVmTask, vm, nix_options)


def run_command(args: argparse.Namespace) -> None:
    flake_url = args.flake_url or args.flake
    vm = asyncio.run(inspect_vm(flake_url=flake_url, flake_attr=args.machine))

    task = run_vm(vm, args.option)
    for line in task.log_lines():
        print(line, end="")


def register_run_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str, help="machine in the flake to run")
    parser.add_argument("--flake_url", type=str, help="flake url")
    parser.set_defaults(func=run_command)
