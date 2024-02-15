import argparse
import importlib
import json
import logging
import os
import random
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory

from ..cmd import Log, run
from ..dirs import module_root, user_cache_dir, vm_state_dir
from ..errors import ClanError
from ..machines.machines import Machine
from ..nix import nix_shell
from ..secrets.generate import generate_secrets
from .inspect import VmConfig, inspect_vm
from .virtiofsd import start_virtiofsd
from .waypipe import start_waypipe

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
    secrets_dir: Path,
    rootfs_img: Path,
    state_img: Path,
    virtiofsd_socket: Path,
    qmp_socket_file: Path,
    qga_socket_file: Path,
) -> QemuCommand:
    kernel_cmdline = [
        (Path(nixos_config["toplevel"]) / "kernel-params").read_text(),
        f'init={nixos_config["toplevel"]}/init',
        f'regInfo={nixos_config["regInfo"]}/registration',
        "console=hvc0",
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
        # speed-up boot by not waiting for the boot menu
        "-boot", "menu=off,strict=on",
        "-device", "virtio-rng-pci",
        "-netdev", "user,id=user.0",
        "-device", "virtio-net-pci,netdev=user.0,romfile=",
        "-chardev", f"socket,id=char1,path={virtiofsd_socket}",
        "-device", "vhost-user-fs-pci,chardev=char1,tag=nix-store",
        "-virtfs", f"local,path={secrets_dir},security_model=none,mount_tag=secrets",
        "-drive", f"cache=writeback,file={rootfs_img},format=qcow2,id=drive1,if=none,index=1,werror=report",
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

        "-serial", "null",
        "-chardev", "stdio,mux=on,id=char0,signal=off",
        "-mon", "chardev=char0,mode=readline",
        "-device", "virtconsole,chardev=char0,nr=0",
    ]  # fmt: on

    vsock_cid = None
    if vm.graphics:
        opts = graphics_options(vm)
        vsock_cid = opts.vsock_cid
        command.extend(opts.args)
    else:
        command.append("-nographic")
    return QemuCommand(command, vsock_cid=vsock_cid)


def facts_to_nixos_config(facts: dict[str, dict[str, bytes]]) -> dict:
    nixos_config: dict = {}
    nixos_config["clanCore"] = {}
    nixos_config["clanCore"]["secrets"] = {}
    for service, service_facts in facts.items():
        nixos_config["clanCore"]["secrets"][service] = {}
        nixos_config["clanCore"]["secrets"][service]["facts"] = {}
        for fact, value in service_facts.items():
            nixos_config["clanCore"]["secrets"][service]["facts"][fact] = {
                "value": value.decode()
            }
    return nixos_config


# TODO move this to the Machines class
def build_vm(
    machine: Machine, vm: VmConfig, tmpdir: Path, nix_options: list[str]
) -> dict[str, str]:
    secrets_dir = get_secrets(machine, tmpdir)

    facts_module = importlib.import_module(machine.facts_module)
    fact_store = facts_module.FactStore(machine=machine)
    facts = fact_store.get_all()

    nixos_config_file = machine.build_nix(
        "config.system.clan.vm.create",
        extra_config=facts_to_nixos_config(facts),
        nix_options=nix_options,
    )
    try:
        vm_data = json.loads(Path(nixos_config_file).read_text())
        vm_data["secrets_dir"] = str(secrets_dir)
        return vm_data
    except json.JSONDecodeError as e:
        raise ClanError(f"Failed to parse vm config: {e}")


def get_secrets(
    machine: Machine,
    tmpdir: Path,
) -> Path:
    secrets_dir = tmpdir / "secrets"
    secrets_dir.mkdir(parents=True, exist_ok=True)

    secrets_module = importlib.import_module(machine.secrets_module)
    secret_store = secrets_module.SecretStore(machine=machine)

    # TODO Only generate secrets for local clans
    generate_secrets(machine)

    secret_store.upload(secrets_dir)
    return secrets_dir


def prepare_disk(
    directory: Path,
    size: str = "1024M",
    file_name: str = "disk.img",
) -> Path:
    disk_img = directory / file_name
    cmd = nix_shell(
        ["nixpkgs#qemu"],
        [
            "qemu-img",
            "create",
            "-f",
            "qcow2",
            str(disk_img),
            size,
        ],
    )
    run(
        cmd,
        log=Log.BOTH,
        error_msg=f"Could not create disk image at {disk_img}",
    )

    return disk_img


def run_vm(vm: VmConfig, nix_options: list[str] = []) -> None:
    machine = Machine(vm.machine_name, vm.flake_url)
    log.debug(f"Creating VM for {machine}")

    # store the temporary rootfs inside XDG_CACHE_HOME on the host
    # otherwise, when using /tmp, we risk running out of memory
    cache = user_cache_dir() / "clan"
    cache.mkdir(exist_ok=True)
    with TemporaryDirectory(dir=cache) as cachedir, TemporaryDirectory() as sockets:
        tmpdir = Path(cachedir)

        # TODO: We should get this from the vm argument
        nixos_config = build_vm(machine, vm, tmpdir, nix_options)

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
                size="50G",
            )
        virtiofsd_socket = Path(sockets) / "virtiofsd.sock"
        qemu_cmd = qemu_command(
            vm,
            nixos_config,
            secrets_dir=Path(nixos_config["secrets_dir"]),
            rootfs_img=rootfs_img,
            state_img=state_img,
            virtiofsd_socket=virtiofsd_socket,
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

        with start_waypipe(
            qemu_cmd.vsock_cid, f"[{vm.machine_name}] "
        ), start_virtiofsd(virtiofsd_socket):
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
