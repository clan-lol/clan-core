import random
from dataclasses import dataclass
from pathlib import Path

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
