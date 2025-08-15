import json
import subprocess
import sys
from contextlib import ExitStack

import pytest
from clan_cli.tests.age_keys import SopsSetup
from clan_cli.tests.fixtures_flakes import ClanFlake
from clan_cli.tests.helpers import cli
from clan_cli.vms.run import inspect_vm, spawn_vm
from clan_lib import cmd
from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_config, nix_eval, run


@pytest.mark.impure
@pytest.mark.skipif(sys.platform == "darwin", reason="preload doesn't work on darwin")
def test_vm_deployment(
    flake: ClanFlake,
    sops_setup: SopsSetup,
) -> None:
    # machine 1
    config = nix_config()
    machine1_config = flake.machines["m1_machine"]
    machine1_config["nixpkgs"]["hostPlatform"] = config["system"]
    machine1_config["clan"]["virtualisation"]["graphics"] = False
    machine1_config["services"]["getty"]["autologinUser"] = "root"
    machine1_config["services"]["openssh"]["enable"] = True
    machine1_config["networking"]["firewall"]["enable"] = False
    machine1_config["users"]["users"]["root"]["openssh"]["authorizedKeys"]["keys"] = [
        # put your key here when debugging and pass ssh_port in run_vm_in_thread call below
    ]
    m1_generator = machine1_config["clan"]["core"]["vars"]["generators"]["m1_generator"]
    m1_generator["files"]["my_secret"]["secret"] = True
    m1_generator["script"] = """
        echo hello > "$out"/my_secret
    """
    m1_shared_generator = machine1_config["clan"]["core"]["vars"]["generators"][
        "my_shared_generator"
    ]
    m1_shared_generator["share"] = True
    m1_shared_generator["files"]["shared_secret"]["secret"] = True
    m1_shared_generator["files"]["no_deploy_secret"]["secret"] = True
    m1_shared_generator["files"]["no_deploy_secret"]["deploy"] = False
    m1_shared_generator["script"] = """
        echo hello > "$out"/shared_secret
        echo hello > "$out"/no_deploy_secret
    """

    flake.refresh()

    sops_setup.init(flake.path)
    cli.run(["vars", "generate", "--flake", str(flake.path)])

    # check sops secrets not empty
    sops_secrets = json.loads(
        run(
            nix_eval(
                [
                    f"{flake.path}#nixosConfigurations.m1_machine.config.sops.secrets",
                ]
            )
        ).stdout.strip()
    )
    assert sops_secrets != {}
    my_secret_path = run(
        nix_eval(
            [
                f"{flake.path}#nixosConfigurations.m1_machine.config.clan.core.vars.generators.m1_generator.files.my_secret.path",
            ]
        )
    ).stdout.strip()
    assert "no-such-path" not in my_secret_path
    shared_secret_path = run(
        nix_eval(
            [
                f"{flake.path}#nixosConfigurations.m1_machine.config.clan.core.vars.generators.my_shared_generator.files.shared_secret.path",
            ]
        )
    ).stdout.strip()
    assert "no-such-path" not in shared_secret_path
    # run nix flake lock
    cmd.run(["nix", "flake", "lock"], cmd.RunOpts(cwd=flake.path))

    vm1_config = inspect_vm(machine=Machine("m1_machine", Flake(str(flake.path))))
    with ExitStack() as stack:
        vm1 = stack.enter_context(spawn_vm(vm1_config, stdin=subprocess.DEVNULL))
        qga_m1 = stack.enter_context(vm1.qga_connect())
        # run these always successful commands to make sure all vms have started before continuing
        qga_m1.run(["echo"])
        # check my_secret is deployed
        result = qga_m1.run(["cat", "/run/secrets/vars/m1_generator/my_secret"])
        assert result.stdout == "hello\n"
        # check shared_secret is deployed on m1
        result = qga_m1.run(
            ["cat", "/run/secrets/vars/my_shared_generator/shared_secret"]
        )
        assert result.stdout == "hello\n"
        # check no_deploy_secret is not deployed
        result = qga_m1.run(
            ["test", "-e", "/run/secrets/vars/my_shared_generator/no_deploy_secret"],
            check=False,
        )
        assert result.returncode != 0
