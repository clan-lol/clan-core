import json
import subprocess
import sys
from contextlib import ExitStack
from pathlib import Path

import pytest
from clan_cli.tests.age_keys import SopsSetup
from clan_cli.tests.helpers import cli
from clan_cli.vms.run import inspect_vm, spawn_vm
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_eval, run


@pytest.mark.with_core
@pytest.mark.skipif(sys.platform == "darwin", reason="preload doesn't work on darwin")
def test_vm_deployment(
    vm_test_flake: Path,
    sops_setup: SopsSetup,
) -> None:
    # Set up sops for the test flake machines
    sops_setup.init(vm_test_flake)
    cli.run(["vars", "generate", "--flake", str(vm_test_flake), "test-vm-deployment"])

    # check sops secrets not empty
    sops_secrets = json.loads(
        run(
            nix_eval(
                [
                    f"{vm_test_flake}#nixosConfigurations.test-vm-deployment.config.sops.secrets",
                ],
            ),
        ).stdout.strip(),
    )
    assert sops_secrets != {}
    my_secret_path = run(
        nix_eval(
            [
                f"{vm_test_flake}#nixosConfigurations.test-vm-deployment.config.clan.core.vars.generators.m1_generator.files.my_secret.path",
            ],
        ),
    ).stdout.strip()
    assert "no-such-path" not in my_secret_path
    shared_secret_path = run(
        nix_eval(
            [
                f"{vm_test_flake}#nixosConfigurations.test-vm-deployment.config.clan.core.vars.generators.my_shared_generator.files.shared_secret.path",
            ],
        ),
    ).stdout.strip()
    assert "no-such-path" not in shared_secret_path

    vm1_config = inspect_vm(
        machine=Machine("test-vm-deployment", Flake(str(vm_test_flake))),
    )
    with ExitStack() as stack:
        vm1 = stack.enter_context(spawn_vm(vm1_config, stdin=subprocess.DEVNULL))
        qga_m1 = stack.enter_context(vm1.qga_connect())
        # run these always successful commands to make sure all vms have started before continuing
        qga_m1.run(["echo"])
        # check all systemd services are OK, or print details
        result = qga_m1.run(
            [
                "/bin/sh",
                "-c",
                "systemctl --failed | tee /tmp/log | grep -q '0 loaded units listed' || ( cat /tmp/log && false )",
            ],
        )
        # check my_secret is deployed
        result = qga_m1.run(["cat", "/run/secrets/vars/m1_generator/my_secret"])
        assert result.stdout == "hello\n"
        # check shared_secret is deployed
        result = qga_m1.run(
            ["cat", "/run/secrets/vars/my_shared_generator/shared_secret"],
        )
        assert result.stdout == "hello\n"
        # check no_deploy_secret is not deployed
        result = qga_m1.run(
            ["test", "-e", "/run/secrets/vars/my_shared_generator/no_deploy_secret"],
            check=False,
        )
        assert result.returncode != 0
