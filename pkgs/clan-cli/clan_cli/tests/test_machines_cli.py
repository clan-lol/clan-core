import pytest
from clan_cli.flake import Flake
from clan_cli.inventory import load_inventory_json
from clan_cli.secrets.folders import sops_machines_folder
from clan_cli.tests import fixtures_flakes
from clan_cli.tests.age_keys import SopsSetup, assert_secrets_file_recipients
from clan_cli.tests.helpers import cli
from clan_cli.tests.stdout import CaptureOutput


@pytest.mark.impure
def test_machine_subcommands(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
    capture_output: CaptureOutput,
) -> None:
    cli.run(
        [
            "machines",
            "create",
            "--flake",
            str(test_flake_with_core.path),
            "machine1",
            "--tags",
            "vm",
        ]
    )

    inventory: dict = dict(load_inventory_json(Flake(str(test_flake_with_core.path))))
    assert "machine1" in inventory["machines"]
    assert "service" not in inventory

    with capture_output as output:
        cli.run(["machines", "list", "--flake", str(test_flake_with_core.path)])

    print(output.out)
    assert "machine1" in output.out
    assert "vm1" in output.out
    assert "vm2" in output.out

    cli.run(
        ["machines", "delete", "--flake", str(test_flake_with_core.path), "machine1"]
    )

    inventory_2: dict = dict(load_inventory_json(Flake(str(test_flake_with_core.path))))
    assert "machine1" not in inventory_2["machines"]
    assert "service" not in inventory_2

    with capture_output as output:
        cli.run(["machines", "list", "--flake", str(test_flake_with_core.path)])
    assert "machine1" not in output.out
    assert "vm1" in output.out
    assert "vm2" in output.out


@pytest.mark.with_core
def test_machine_delete(
    monkeypatch: pytest.MonkeyPatch,
    flake_with_sops: fixtures_flakes.ClanFlake,
    sops_setup: SopsSetup,
) -> None:
    flake = flake_with_sops

    admin_key, machine_key, machine2_key, *xs = sops_setup.keys

    # create a couple machines with their keys
    for name, key in (("my-machine", machine_key), ("my-machine2", machine2_key)):
        cli.run(["machines", "create", f"--flake={flake.path}", name])
        add_machine_key = [
            "secrets",
            "machines",
            "add",
            f"--flake={flake.path}",
            name,
            key.pubkey,
        ]
        cli.run(add_machine_key)

    # create a secret shared by both machines
    shared_secret_name = "shared_secret"
    with monkeypatch.context():
        monkeypatch.setenv("SOPS_NIX_SECRET", "secret_value")
        set_shared_secret = [
            "secrets",
            "set",
            f"--flake={flake.path}",
            "--machine=my-machine",
            "--machine=my-machine2",
            shared_secret_name,
        ]
        cli.run(set_shared_secret)

    my_machine_sops_folder = sops_machines_folder(flake.path) / "my-machine"
    assert my_machine_sops_folder.is_dir(), (
        "A sops folder for `my-machine` should have been created with its public key"
    )

    # define some vars generator for `my-machine`:
    config = flake.machines["my-machine"]
    config["nixpkgs"]["hostPlatform"] = "x86_64-linux"
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_value"]["secret"] = False
    my_generator["files"]["my_secret"]["secret"] = True
    my_generator["script"] = (
        'echo -n public > "$out"/my_value;'
        'echo -n secret > "$out"/my_secret;'
        'echo -n non-default > "$out"/value_with_default'
    )
    flake.refresh()  # saves "my_generator"
    monkeypatch.chdir(flake.path)

    cli.run(["vars", "generate", "--flake", str(flake.path), "my-machine"])
    my_machine_vars_store = flake.path / "vars/per-machine" / "my-machine"
    assert my_machine_vars_store.is_dir(), (
        "A vars directory should have been created for `my-machine`"
    )

    cli.run(["machines", "delete", "--flake", str(flake.path), "my-machine"])
    assert not my_machine_vars_store.exists(), (
        "The vars directory for `my-machine` should have been deleted"
    )
    assert not my_machine_sops_folder.exists(), (
        "The sops folder holding the public key for `my-machine` should have been deleted"
    )
    expected_recipients = [admin_key, machine2_key]
    assert_secrets_file_recipients(flake.path, shared_secret_name, expected_recipients)
