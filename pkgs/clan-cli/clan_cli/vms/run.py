import argparse
import contextlib
import importlib
import json
import logging
import os
import random
import socket
import subprocess
import time
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory

from ..cmd import Log, run
from ..dirs import machine_gcroot, module_root, user_cache_dir, vm_state_dir
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

    if vm.waypipe:
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
    rootfs_img: Path,
    state_img: Path,
    qmp_socket_file: Path,
    qga_socket_file: Path,
) -> QemuCommand:
    kernel_cmdline = [
        (Path(nixos_config["toplevel"]) / "kernel-params").read_text(),
        f'init={nixos_config["toplevel"]}/init',
        f'regInfo={nixos_config["regInfo"]}/registration',
        "console=ttyS0,115200n8",
    ]
    if not vm.waypipe:
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
        "-drive", f"cache=writeback,file={rootfs_img},format=raw,id=drive1,if=none,index=1,werror=report",
        "-device", "virtio-blk-pci,bootindex=1,drive=drive1,serial=root",
        "-drive", f"cache=writeback,file={state_img},format=qcow2,id=state,if=none,index=2,werror=report",
        "-device", "virtio-blk-pci,drive=state",
        "-device", "virtio-keyboard",
        "-usb", "-device", "usb-tablet,bus=usb-bus.0",
        "-kernel", f'{nixos_config["toplevel"]}/kernel',
        "-initrd", nixos_config["initrd"],
        "-append", " ".join(kernel_cmdline),
        # qmp & qga setup
        "-qmp", f"unix:{qmp_socket_file},server,wait=off",
        "-chardev", f"socket,path={qga_socket_file},server=on,wait=off,id=qga0",
        "-device", "virtio-serial",
        "-device", "virtserialport,chardev=qga0,name=org.qemu.guest_agent.0",
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
def build_vm(machine: Machine, vm: VmConfig, nix_options: list[str]) -> dict[str, str]:
    config = nix_config()
    system = config["system"]

    clan_dir = machine.flake
    cmd = nix_build(
        [
            f'{clan_dir}#clanInternals.machines."{system}"."{machine.name}".config.system.clan.vm.create',
            *nix_options,
        ],
        machine_gcroot(flake_url=str(vm.flake_url)) / f"vm-{machine.name}",
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


def prepare_disk(
    directory: Path,
    disk_format: str = "raw",
    size: str = "1024M",
    label: str = "nixos",
    file_name: str = "disk.img",
) -> Path:
    disk_img = directory / file_name
    cmd = nix_shell(
        ["nixpkgs#qemu"],
        [
            "qemu-img",
            "create",
            "-f",
            disk_format,
            str(disk_img),
            size,
        ],
    )
    run(
        cmd,
        log=Log.BOTH,
        error_msg=f"Could not create disk image at {disk_img}",
    )

    if disk_format == "raw":
        cmd = nix_shell(
            ["nixpkgs#e2fsprogs"],
            [
                "mkfs.ext4",
                "-L",
                label,
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


def run_vm(vm: VmConfig, nix_options: list[str] = []) -> None:
    machine = Machine(vm.machine_name, vm.flake_url)
    log.debug(f"Creating VM for {machine}")

    # TODO: We should get this from the vm argument
    nixos_config = build_vm(machine, vm, nix_options)

    # store the temporary rootfs inside XDG_CACHE_HOME on the host
    # otherwise, when using /tmp, we risk running out of memory
    cache = user_cache_dir() / "clan"
    cache.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=cache) as cachedir, TemporaryDirectory() as sockets:
        tmpdir = Path(cachedir)
        xchg_dir = tmpdir / "xchg"
        xchg_dir.mkdir(exist_ok=True)

        secrets_dir = get_secrets(machine, tmpdir)

        state_dir = vm_state_dir(str(vm.flake_url), machine.name)
        state_dir.mkdir(parents=True, exist_ok=True)

        # specify socket files for qmp and qga
        qmp_socket_file = Path(sockets) / "qmp.sock"
        qga_socket_file = Path(sockets) / "qga.sock"
        # Create symlinks to the qmp/qga sockets to be able to find them later.
        # This indirection is needed because we cannot put the sockets directly
        #   in the state_dir.
        # The reason is, qemu has a length limit of 108 bytes for the qmp socket
        #   path which is violated easily.
        qmp_link = state_dir / "qmp.sock"
        if os.path.lexists(qmp_link):
            qmp_link.unlink()
        qmp_link.symlink_to(qmp_socket_file)

        qga_link = state_dir / "qga.sock"
        if os.path.lexists(qga_link):
            qga_link.unlink()
        qga_link.symlink_to(qga_socket_file)

        rootfs_img = prepare_disk(tmpdir)
        state_img = state_dir / "state.qcow2"
        if not state_img.exists():
            state_img = prepare_disk(
                directory=state_dir,
                file_name="state.qcow2",
                disk_format="qcow2",
                size="50G",
                label="state",
            )
        qemu_cmd = qemu_command(
            vm,
            nixos_config,
            xchg_dir=xchg_dir,
            secrets_dir=secrets_dir,
            rootfs_img=rootfs_img,
            state_img=state_img,
            qmp_socket_file=qmp_socket_file,
            qga_socket_file=qga_socket_file,
        )

        packages = ["nixpkgs#qemu"]

        env = os.environ.copy()
        if vm.graphics and not vm.waypipe:
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
    waypipe: bool = False


def run_command(args: argparse.Namespace) -> None:
    run_options = RunOptions(
        machine=args.machine,
        flake=args.flake,
        nix_options=args.option,
    )

    machine = Machine(run_options.machine, run_options.flake)

    vm = inspect_vm(machine=machine)

    run_vm(vm, run_options.nix_options)


def register_run_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("machine", type=str, help="machine in the flake to run")
    parser.add_argument("--flake-url", type=str, help="flake url")
    parser.set_defaults(func=run_command)
