from pathlib import Path

import pytest
from age_keys import SopsSetup
from fixtures_flakes import generate_flake
from helpers import cli
from helpers.nixos_config import nested_dict
from helpers.vms import qga_connect, run_vm_in_thread, wait_vm_down
from root import CLAN_CORE


@pytest.mark.impure
def test_vm_deployment(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    sops_setup: SopsSetup,
) -> None:
    config = nested_dict()
    config["clan"]["virtualisation"]["graphics"] = False
    config["services"]["getty"]["autologinUser"] = "root"
    config["services"]["openssh"]["enable"] = True
    config["networking"]["firewall"]["enable"] = False
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_secret"]["secret"] = True
    my_generator["files"]["my_value"]["secret"] = False
    my_generator["script"] = "echo hello > $out/my_secret && echo hello > $out/my_value"
    flake = generate_flake(
        temporary_home,
        flake_template=CLAN_CORE / "templates" / "minimal",
        machine_configs=dict(my_machine=config),
    )
    monkeypatch.chdir(flake.path)
    sops_setup.init()
    cli.run(["vars", "generate", "my_machine"])
    run_vm_in_thread("my_machine")
    qga = qga_connect("my_machine")
    qga.run("ls /run/secrets/my_machine/my_generator/my_secret", check=True)
    _, out, _ = qga.run("cat /run/secrets/my_machine/my_generator/my_secret")
    assert out == "hello\n"
    qga.exec_cmd("poweroff")
    wait_vm_down("my_machine")
