import platform
import random
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from clan_lib.errors import ClanError
from clan_lib.nix import nix_test_store

from clan_cli.qemu.qmp import QEMUMonitorProtocol

from .inspect import VmConfig


@dataclass
class GraphicOptions:
    args: list[str]
    vsock_cid: int | None = None


def graphics_options(vm: VmConfig) -> GraphicOptions:
    common = [
        "-audio",
        "driver=pa,model=virtio",
    ]

    if vm.waypipe.enable:
        # FIXME: check for collisions
        cid = random.randint(1, 2**32)
        # fmt: off
        return GraphicOptions([
          *common,
          "-nographic",
          "-device", f"vhost-vsock-pci,id=vhost-vsock-pci0,guest-cid={cid}",
          "-vga", "none",
          #"-display", "egl-headless,gl=core",

          # this would make the gpu part of the hypervisor
          #"-device", "virtio-vga-gl,blob=true",

          # This is for an external gpu process
          #"-device", "virtio-serial-pci",
          #"-device", "vhost-user-vga,chardev=vgpu",
          #"-chardev", "socket,id=vgpu,path=/tmp/vgpu.sock",
        ], cid)
        # fmt: on
    if Path("/run/opengl-driver").exists():
        display_options = [
            "-vga",
            "none",
            "-display",
            "gtk,gl=on",
            "-device",
            "virtio-gpu-gl",
            "-display",
            "spice-app,gl=on",
        ]
    else:
        display_options = ["-display", "spice-app"]

    # fmt: off
    return GraphicOptions([
        *common,
        *display_options,
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


def get_machine_options() -> str:
    """Get appropriate QEMU machine options for host architecture."""
    arch = platform.machine().lower()
    system = platform.system().lower()

    # Determine accelerator based on OS
    if system == "darwin":
        # macOS uses Hypervisor.framework
        accel = "hvf"
    else:
        # Linux and others use KVM
        accel = "kvm"

    if arch in ("x86_64", "amd64", "i386", "i686"):
        # For x86_64, use q35 for modern PCIe support
        return f"q35,memory-backend=mem,accel={accel}"
    if arch in ("aarch64", "arm64"):
        # Use virt machine type for ARM64
        if system == "darwin":
            # macOS ARM uses GIC version 2
            return f"virt,gic-version=2,memory-backend=mem,accel={accel}"
        # Linux ARM uses max GIC version
        return f"virt,gic-version=max,memory-backend=mem,accel={accel}"
    if arch == "armv7l":
        # 32-bit ARM
        return f"virt,memory-backend=mem,accel={accel}"
    if arch in ("riscv64", "riscv32"):
        # RISC-V architectures
        return f"virt,memory-backend=mem,accel={accel}"
    if arch in ("powerpc64le", "powerpc64", "ppc64le", "ppc64"):
        # PowerPC architectures
        return f"powernv,memory-backend=mem,accel={accel}"

    # No fallback - raise an error for unsupported architectures
    msg = f"Unsupported architecture: {arch} on {system}. Supported architectures are: x86_64, aarch64, armv7l, riscv64, riscv32, powerpc64"
    raise ClanError(msg)


def qemu_command(
    vm: VmConfig,
    nixos_config: dict[str, str],
    secrets_dir: Path,
    rootfs_img: Path,
    state_img: Path,
    virtiofsd_socket: Path,
    qmp_socket_file: Path,
    qga_socket_file: Path,
    portmap: dict[int, int] | None = None,
    interactive: bool = False,
) -> QemuCommand:
    if portmap is None:
        portmap = {}

    toplevel = Path(nixos_config["toplevel"])
    chroot_toplevel = toplevel
    initrd = Path(nixos_config["initrd"])
    if tmp_store := nix_test_store():
        chroot_toplevel = tmp_store / toplevel.relative_to("/")
        initrd = tmp_store / initrd.relative_to("/")

    kernel_cmdline = [
        (chroot_toplevel / "kernel-params").read_text(),
        f"init={toplevel}/init",
        f"regInfo={nixos_config['regInfo']}/registration",
        "console=hvc0",
    ]
    if not vm.waypipe.enable:
        kernel_cmdline.append("console=tty0")
    hostfwd = ",".join(f"hostfwd=tcp::{h}-:{g}" for h, g in portmap.items())
    machine_options = get_machine_options()
    # fmt: off
    command = [
        "qemu-kvm",
        "-name", vm.machine_name,
        "-m", f'{nixos_config["memorySize"]}M',
        "-object", f"memory-backend-memfd,id=mem,size={nixos_config['memorySize']}M",
        "-machine", machine_options,
        "-smp", str(nixos_config["cores"]),
        "-cpu", "max",
        "-enable-kvm",
        # speed-up boot by not waiting for the boot menu
        "-boot", "menu=off,strict=on",
        "-device", "virtio-rng-pci",
        "-netdev", f"user,id=user.0,{hostfwd}",
        "-device", "virtio-net-pci,netdev=user.0,romfile=",
        "-chardev", f"socket,id=char1,path={virtiofsd_socket}",
        "-device", "vhost-user-fs-pci,chardev=char1,tag=nix-store",
        "-virtfs", f"local,path={secrets_dir},security_model=none,mount_tag=secrets",
        "-drive", f"cache=writeback,file={rootfs_img},format=qcow2,id=drive1,if=none,index=1,werror=report",
        "-device", "virtio-blk-pci,bootindex=1,drive=drive1,serial=root",
        "-drive", f"cache=writeback,file={state_img},format=qcow2,id=state,if=none,index=2,werror=report",
        "-device", "virtio-blk-pci,drive=state",
        "-device", "virtio-keyboard",
        "-kernel", f"{chroot_toplevel}/kernel",
        "-initrd", str(initrd),
        "-append", " ".join(kernel_cmdline),
        # qmp & qga setup
        "-qmp", f"unix:{qmp_socket_file},server,wait=off",
        "-chardev", f"socket,path={qga_socket_file},server=on,wait=off,id=qga0",
        "-device", "virtio-serial",
        "-device", "virtserialport,chardev=qga0,name=org.qemu.guest_agent.0",
    ]
    # USB tablet only works reliably on x86_64 Linux for now, not aarch64-linux.
    # TODO: Fix USB tablet support for ARM architectures and test macOS
    if platform.system().lower() == "linux" and platform.machine().lower() in ("x86_64", "amd64"):
        command.extend(["-usb", "-device", "usb-tablet,bus=usb-bus.0"])

    if interactive:
        command.extend(
            [
                "-serial",
                "null",
                "-chardev",
                "stdio,mux=on,id=char0,signal=off",
                "-mon",
                "chardev=char0,mode=readline",
                "-device",
                "virtconsole,chardev=char0,nr=0",
            ],
        )
    else:
        command.extend(
            [
                "-serial",
                "null",
                "-chardev",
                "file,id=char0,path=/dev/stdout",
                "-device",
                "virtconsole,chardev=char0,nr=0",
                "-monitor",
                "none",
            ],
        )

    vsock_cid = None
    if vm.graphics:
        opts = graphics_options(vm)
        vsock_cid = opts.vsock_cid
        command.extend(opts.args)
    else:
        command.append("-nographic")
    return QemuCommand(command, vsock_cid=vsock_cid)


class QMPWrapper:
    def __init__(self, state_dir: Path) -> None:
        # These sockets here are just symlinks to the real sockets which
        # are created by the run.py file. The reason being that we run into
        # file path length issues on Linux. If no qemu process is running
        # the symlink will be dangling.
        self._qmp_socket: Path = state_dir / "qmp.sock"
        self._qga_socket: Path = state_dir / "qga.sock"

    @contextmanager
    def qmp_ctx(self) -> Generator[QEMUMonitorProtocol]:
        rpath = self._qmp_socket.resolve()
        if not rpath.exists():
            msg = f"qmp socket {rpath} does not exist. Is the VM running?"
            raise ClanError(msg)
        qmp = QEMUMonitorProtocol(str(rpath))
        qmp.connect()
        try:
            yield qmp
        finally:
            qmp.close()
