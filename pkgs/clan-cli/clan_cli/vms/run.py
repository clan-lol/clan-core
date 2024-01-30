import argparse
import contextlib
import importlib
import json
import logging
import os
import random
import socket
import subprocess
import tempfile
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO

from ..cmd import Log, run
from ..dirs import machine_gcroot, module_root, vm_state_dir
from ..errors import ClanError
from ..machines.machines import Machine
from ..nix import nix_build, nix_config, nix_shell
from ..secrets.generate import generate_secrets
from .inspect import VmConfig, inspect_vm

log = logging.getLogger(__name__)


@dataclass
class GraphicOptions:
    args: list[str]
    vsock_cid: int | None = None


def graphics_options(vm: VmConfig) -> GraphicOptions:
    common = [
        "-audio",
        "driver=pa,model=virtio",
    ]

    if vm.wayland:
        # FIXME: check for collisions
        cid = random.randint(1, 2**32)
        # fmt: off
        return GraphicOptions([
          *common,
          "-nographic",
          "-vga", "none",
          "-device", f"vhost-vsock-pci,id=vhost-vsock-pci0,guest-cid={cid}",
          # TODO: vgpu
          #"-display", "egl-headless,gl=core",
          #"-device", "virtio-vga,blob=true",
          #"-device", "virtio-serial-pci",
          #"-device", "vhost-user-vga,chardev=vgpu",
          #"-chardev", "socket,id=vgpu,path=/tmp/vgpu.sock",
        ], cid)
        # fmt: on
    else:
        # fmt: off
        return GraphicOptions([
            *common,
            "-vga", "none",
            "-display", "gtk,gl=on",
            "-device", "virtio-gpu-gl",
            "-display", "spice-app,gl=on",
            "-device", "virtio-serial-pci",
            "-chardev", "spicevmc,id=vdagent0,name=vdagent",
            "-device", "virtserialport,chardev=vdagent0,name=com.redhat.spice.0",
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
        ], None)
        # fmt: on


@dataclass
class QemuCommand:
    args: list[str]
    vsock_cid: int | None = None


def qemu_command(
    vm: VmConfig,
    nixos_config: dict[str, str],
    xchg_dir: Path,
    secrets_dir: Path,
    state_dir: Path,
    disk_img: Path,
) -> QemuCommand:
    kernel_cmdline = [
        (Path(nixos_config["toplevel"]) / "kernel-params").read_text(),
        f'init={nixos_config["toplevel"]}/init',
        f'regInfo={nixos_config["regInfo"]}/registration',
        "console=ttyS0,115200n8",
    ]
    if not vm.wayland:
        kernel_cmdline.append("console=tty0")
    # fmt: off
    command = [
        "qemu-kvm",
        "-name", vm.machine_name,
        "-m", f'{nixos_config["memorySize"]}M',
        "-object", f"memory-backend-memfd,id=mem,size={nixos_config['memorySize']}M",
        "-machine", "pc,memory-backend=mem,accel=kvm",
        "-smp", str(nixos_config["cores"]),
        "-cpu", "max",
        "-enable-kvm",
        "-device", "virtio-rng-pci",
        "-net", "nic,netdev=user.0,model=virtio",
        "-netdev", "user,id=user.0",
        "-virtfs", "local,path=/nix/store,security_model=none,mount_tag=nix-store",
        "-virtfs", f"local,path={xchg_dir},security_model=none,mount_tag=shared",
        "-virtfs", f"local,path={xchg_dir},security_model=none,mount_tag=xchg",
        "-virtfs", f"local,path={secrets_dir},security_model=none,mount_tag=secrets",
        "-virtfs", f"local,path={state_dir},security_model=none,mount_tag=state",
        "-drive", f"cache=writeback,file={disk_img},format=raw,id=drive1,if=none,index=1,werror=report",
        "-device", "virtio-blk-pci,bootindex=1,drive=drive1,serial=root",
        "-device", "virtio-keyboard",
        "-usb", "-device", "usb-tablet,bus=usb-bus.0",
        "-kernel", f'{nixos_config["toplevel"]}/kernel',
        "-initrd", nixos_config["initrd"],
        "-append", " ".join(kernel_cmdline),
    ]  # fmt: on

    vsock_cid = None
    if vm.graphics:
        opts = graphics_options(vm)
        vsock_cid = opts.vsock_cid
        command.extend(opts.args)
    else:
        command.append("-nographic")
    return QemuCommand(command, vsock_cid=vsock_cid)


# TODO move this to the Machines class
def get_vm_create_info(
    machine: Machine, vm: VmConfig, nix_options: list[str]
) -> dict[str, str]:
    config = nix_config()
    system = config["system"]

    clan_dir = machine.flake
    cmd = nix_build(
        [
            f'{clan_dir}#clanInternals.machines."{system}"."{machine.name}".config.system.clan.vm.create',
            *nix_options,
        ],
        machine_gcroot(clan_name=vm.clan_name, flake_url=str(vm.flake_url))
        / f"vm-{machine.name}",
    )
    proc = run(
        cmd, log=Log.BOTH, error_msg=f"Could not build vm config for {machine.name}"
    )
    try:
        return json.loads(Path(proc.stdout.strip()).read_text())
    except json.JSONDecodeError as e:
        raise ClanError(f"Failed to parse vm config: {e}")


def get_secrets(
    machine: Machine,
    tmpdir: Path,
) -> Path:
    secrets_dir = tmpdir / "secrets"
    secrets_dir.mkdir(exist_ok=True)

    secrets_module = importlib.import_module(machine.secrets_module)
    secret_store = secrets_module.SecretStore(machine=machine)

    # Only generate secrets for local clans
    if isinstance(machine.flake, Path) and machine.flake.is_dir():
        generate_secrets(machine)
    else:
        log.warning("won't generate secrets for non local clan")

    secret_store.upload(secrets_dir)
    return secrets_dir


def prepare_disk(tmpdir: Path, log_fd: IO[str] | None) -> Path:
    disk_img = tmpdir / "disk.img"
    cmd = nix_shell(
        ["nixpkgs#qemu"],
        [
            "qemu-img",
            "create",
            "-f",
            "raw",
            str(disk_img),
            "1024M",
        ],
    )
    run(
        cmd,
        log=Log.BOTH,
        error_msg=f"Could not create disk image at {disk_img}",
    )

    cmd = nix_shell(
        ["nixpkgs#e2fsprogs"],
        [
            "mkfs.ext4",
            "-L",
            "nixos",
            str(disk_img),
        ],
    )
    run(
        cmd,
        log=Log.BOTH,
        error_msg=f"Could not create ext4 filesystem at {disk_img}",
    )
    return disk_img


VMADDR_CID_HYPERVISOR = 2


def test_vsock_port(port: int) -> bool:
    try:
        s = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        s.connect((VMADDR_CID_HYPERVISOR, port))
        s.close()
        return True
    except OSError:
        return False


@contextlib.contextmanager
def start_waypipe(cid: int | None, title_prefix: str) -> Iterator[None]:
    if cid is None:
        yield
        return
    waypipe = nix_shell(
        ["git+https://git.clan.lol/clan/clan-core#waypipe"],
        [
            "waypipe",
            "--vsock",
            "--socket",
            f"s{cid}:3049",
            "--title-prefix",
            title_prefix,
            "client",
        ],
    )
    with subprocess.Popen(waypipe) as proc:
        try:
            while not test_vsock_port(3049):
                time.sleep(0.1)
            yield
        finally:
            proc.kill()


def run_vm(
    vm: VmConfig,
    nix_options: list[str] = [],
    log_fd: IO[str] | None = None,
) -> None:
    """
    log_fd can be used to stream the output of all commands to a UI
    """
    machine = Machine(vm.machine_name, vm.flake_url)
    log.debug(f"Creating VM for {machine}")

    # TODO: We should get this from the vm argument
    nixos_config = get_vm_create_info(machine, vm, nix_options)

    with tempfile.TemporaryDirectory() as tmpdir_:
        tmpdir = Path(tmpdir_)
        xchg_dir = tmpdir / "xchg"
        xchg_dir.mkdir(exist_ok=True)

        secrets_dir = get_secrets(machine, tmpdir)
        disk_img = prepare_disk(tmpdir, log_fd)

        state_dir = vm_state_dir(vm.clan_name, str(machine.flake), machine.name)
        state_dir.mkdir(parents=True, exist_ok=True)

        qemu_cmd = qemu_command(
            vm,
            nixos_config,
            xchg_dir=xchg_dir,
            secrets_dir=secrets_dir,
            state_dir=state_dir,
            disk_img=disk_img,
        )

        packages = ["nixpkgs#qemu"]

        env = os.environ.copy()
        if vm.graphics and not vm.wayland:
            packages.append("nixpkgs#virt-viewer")
            remote_viewer_mimetypes = module_root() / "vms" / "mimetypes"
            env[
                "XDG_DATA_DIRS"
            ] = f"{remote_viewer_mimetypes}:{env.get('XDG_DATA_DIRS', '')}"

        with start_waypipe(qemu_cmd.vsock_cid, f"[{vm.machine_name}] "):
            run(
                nix_shell(packages, qemu_cmd.args),
                env=env,
                log=Log.BOTH,
                error_msg=f"Could not start vm {machine}",
            )


@dataclass
class RunOptions:
    machine: str
    flake: Path
    nix_options: list[str] = field(default_factory=list)
    wayland: bool = False


def run_command(args: argparse.Namespace) -> None:
    run_options = RunOptions(
        machine=args.machine,
        flake=args.flake,
        nix_options=args.option,
        wayland=args.wayland,
    )

    machine = Machine(run_options.machine, run_options.flake)

    vm = inspect_vm(machine=machine)
    # TODO: allow to set this in the config
    vm.wayland = run_options.wayland

    run_vm(vm, run_options.nix_options)


def register_run_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str, help="machine in the flake to run")
    parser.add_argument("--flake-url", type=str, help="flake url")
    parser.add_argument("--wayland", action="store_true", help="use wayland")
    parser.set_defaults(func=run_command)
