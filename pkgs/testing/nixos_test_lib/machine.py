"""VM machine management utilities"""


def create_test_machine(oldmachine, qemu_test_bin: str, **kwargs):
    """Create a new test machine from an installed disk image"""
    start_command = [
        f"{qemu_test_bin}/bin/qemu-kvm",
        "-cpu",
        "max",
        "-m",
        "3048",
        "-virtfs",
        "local,path=/nix/store,security_model=none,mount_tag=nix-store",
        "-drive",
        f"file={oldmachine.state_dir}/target.qcow2,id=drive1,if=none,index=1,werror=report",
        "-device",
        "virtio-blk-pci,drive=drive1",
        "-netdev",
        "user,id=net0",
        "-device",
        "virtio-net-pci,netdev=net0",
    ]
    machine = create_machine(start_command=" ".join(start_command), **kwargs)
    driver.machines.append(machine)
    return machine
