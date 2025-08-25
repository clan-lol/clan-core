# ruff: noqa: SLF001
import pytest
from clan_cli.secrets.folders import sops_machines_folder
from clan_cli.tests import fixtures_flakes
from clan_cli.tests.age_keys import SopsSetup, assert_secrets_file_recipients
from clan_cli.tests.helpers import cli
from clan_cli.tests.stdout import CaptureOutput
from clan_lib.flake import Flake
from clan_lib.persist.inventory_store import InventoryStore


@pytest.mark.with_core
def test_machine_subcommands(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
    capture_output: CaptureOutput,
) -> None:
    inventory_store = InventoryStore(Flake(str(test_flake_with_core.path)))
    inventory = inventory_store.read()
    assert "machine1" not in inventory.get("machines", {})

    cli.run(
        [
            "machines",
            "create",
            "--flake",
            str(test_flake_with_core.path),
            "machine1",
            "--tags",
            "vm",
        ],
    )
    # Usually this is done by `inventory.write` but we created a separate flake object in the test that now holds stale data
    inventory_store._flake.invalidate_cache()

    inventory = inventory_store.read()
    persisted_inventory = inventory_store._get_persisted()
    assert "machine1" in inventory.get("machines", {})

    assert "services" not in persisted_inventory

    with capture_output as output:
        cli.run(["machines", "list", "--flake", str(test_flake_with_core.path)])

    print(output.out)
    assert "machine1" in output.out
    assert "vm1" in output.out
    assert "vm2" in output.out

    cli.run(
        ["machines", "delete", "--flake", str(test_flake_with_core.path), "machine1"],
    )
    # See comment above
    inventory_store._flake.invalidate_cache()

    inventory_2: dict = dict(inventory_store.read())
    assert "machine1" not in inventory_2["machines"]

    persisted_inventory = inventory_store._get_persisted()
    assert "services" not in persisted_inventory

    with capture_output as output:
        cli.run(["machines", "list", "--flake", str(test_flake_with_core.path)])
    assert "machine1" not in output.out
    assert "vm1" in output.out
    assert "vm2" in output.out


@pytest.mark.with_core
def test_machines_update_with_tags(
    test_flake_with_core: fixtures_flakes.FlakeForTest,  # noqa: ARG001
) -> None:
    import argparse

    from clan_cli.machines.update import register_update_parser

    parser = argparse.ArgumentParser()
    register_update_parser(parser)

    args = parser.parse_args(["--tags", "vm", "production"])
    assert hasattr(args, "tags")
    assert args.tags == ["vm", "production"]

    args = parser.parse_args(["machine1", "machine2"])
    assert hasattr(args, "tags")
    assert args.tags == []

    args = parser.parse_args(["machine1", "--tags", "vm"])
    assert args.machines == ["machine1"]
    assert args.tags == ["vm"]


@pytest.mark.with_core
def test_machines_update_nonexistent_machine(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    """Test that update command gives helpful error messages for non-existent machines."""
    from clan_lib.errors import ClanError

    with pytest.raises(ClanError) as exc_info:
        cli.run(
            [
                "machines",
                "update",
                "--flake",
                str(test_flake_with_core.path),
                "nonexistent-machine",
            ],
        )

    error_message = str(exc_info.value)
    assert "nonexistent-machine" in error_message
    assert "not found." in error_message
    # Should suggest similar machines (vm1, vm2 exist in test flake)
    assert "Did you mean:" in error_message or "Available machines:" in error_message


@pytest.mark.with_core
def test_machines_update_typo_in_machine_name(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    """Test that update command suggests similar machine names for typos."""
    from clan_lib.errors import ClanError

    with pytest.raises(ClanError) as exc_info:
        cli.run(
            [
                "machines",
                "update",
                "--flake",
                str(test_flake_with_core.path),
                "v1",  # typo of "vm1"
            ],
        )

    error_message = str(exc_info.value)
    assert "v1" in error_message
    assert "not found." in error_message
    assert "Did you mean:" in error_message
    # Should suggest vm1 as it's the closest match
    assert "vm1" in error_message


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
