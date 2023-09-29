import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from ..dirs import get_clan_flake_toplevel
from ..nix import nix_build, nix_shell


def get_vm_create_info(machine: str) -> dict:
    clan_dir = get_clan_flake_toplevel().as_posix()

    # config = nix_config()
    # system = config["system"]

    vm_json = subprocess.run(
        nix_build(
            [
                # f'{clan_dir}#clanInternals.machines."{system}"."{machine}".config.clan.virtualisation.createJSON' # TODO use this
                f'{clan_dir}#nixosConfigurations."{machine}".config.system.clan.vm.create'
            ]
        ),
        stdout=subprocess.PIPE,
        check=True,
        text=True,
    ).stdout.strip()
    with open(vm_json) as f:
        return json.load(f)


def create(args: argparse.Namespace) -> None:
    print(f"Creating VM for {args.machine}")
    machine = args.machine
    vm_config = get_vm_create_info(machine)
    with tempfile.TemporaryDirectory() as tmpdir_:
        xchg_dir = Path(tmpdir_) / "xchg"
        xchg_dir.mkdir()
        disk_img = f"{tmpdir_}/disk.img"
        subprocess.run(
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
            ),
            stdout=subprocess.PIPE,
            check=True,
            text=True,
        )
        subprocess.run(
            [
                "mkfs.ext4",
                "-L",
                "nixos",
                disk_img,
            ],
            stdout=subprocess.PIPE,
            check=True,
            text=True,
        )

        subprocess.run(
            nix_shell(
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
            ),
            stdout=subprocess.PIPE,
            check=True,
            text=True,
        )


def register_create_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str)
    parser.set_defaults(func=create)
