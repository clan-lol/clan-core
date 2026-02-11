from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from clan_cli.tests.helpers import cli
from clan_cli.vms.run import spawn_vm
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine

if TYPE_CHECKING:
    from .age_keys import KeyPair

no_kvm = not Path("/dev/kvm").exists()


@pytest.mark.skipif(no_kvm, reason="Requires KVM")
@pytest.mark.with_core
def test_run(
    monkeypatch: pytest.MonkeyPatch,
    vm_test_flake: Path,
    age_keys: list["KeyPair"],
) -> None:
    with monkeypatch.context():
        monkeypatch.chdir(vm_test_flake)
        monkeypatch.setenv("SOPS_AGE_KEY", age_keys[0].privkey)

        cli.run(
            [
                "secrets",
                "users",
                "add",
                "user1",
                age_keys[0].pubkey,
            ],
        )
        cli.run(
            [
                "secrets",
                "groups",
                "add-user",
                "admins",
                "user1",
            ],
        )
        cli.run(
            [
                "vms",
                "run",
                "--no-block",
                "test-vm-deployment",
                "-c",
                "shutdown",
                "-h",
                "now",
            ],
        )


@pytest.mark.skipif(no_kvm, reason="Requires KVM")
@pytest.mark.with_core
def test_vm_persistence(
    vm_test_flake: Path,
) -> None:
    machine = Machine("test-vm-persistence", Flake(str(vm_test_flake)))

    with spawn_vm(machine) as vm, vm.qga_connect() as qga:
        # create state via qmp command instead of systemd service
        qga.run(["/bin/sh", "-c", "echo 'dream2nix' > /var/my-state/root"])
        qga.run(["/bin/sh", "-c", "echo 'dream2nix' > /var/my-state/test"])
        qga.run(["/bin/sh", "-c", "chown test /var/my-state/test"])
        qga.run(["/bin/sh", "-c", "chown test /var/user-state"])
        qga.run_nonblocking(["shutdown", "-h", "now"])

    ## start vm again
    with spawn_vm(machine) as vm, vm.qga_connect() as qga:
        # check state exists
        qga.run(["cat", "/var/my-state/test"])
        # ensure root file is owned by root
        qga.run(["stat", "-c", "%U", "/var/my-state/root"])
        # ensure test file is owned by test
        qga.run(["stat", "-c", "%U", "/var/my-state/test"])
        # ensure /var/user-state is owned by test
        qga.run(["stat", "-c", "%U", "/var/user-state"])

        # ensure that the file created by the service is still there and has the expected content
        result = qga.run(["cat", "/var/my-state/test"])
        assert result.stdout == "dream2nix\n", result.stdout

        # check for errors
        result = qga.run(["cat", "/var/my-state/error"], check=False)
        assert result.returncode == 1, result.stdout

        # check all systemd services are OK, or print details
        result = qga.run(
            [
                "/bin/sh",
                "-c",
                "systemctl --failed | tee /tmp/log | grep -q '0 loaded units listed' || ( cat /tmp/log && false )",
            ],
        )
