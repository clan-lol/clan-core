import os
from collections import defaultdict
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from age_keys import SopsSetup
from fixtures_flakes import generate_flake
from helpers import cli
from root import CLAN_CORE

from clan_cli.clan_uri import FlakeId
from clan_cli.machines.machines import Machine
from clan_cli.vars.secret_modules.sops import SecretStore


def def_value() -> defaultdict:
    return defaultdict(def_value)


# allows defining nested dictionary in a single line
nested_dict: Callable[[], dict[str, Any]] = lambda: defaultdict(def_value)


@pytest.mark.impure
def test_generate_public_var(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    # age_keys: list["KeyPair"],
) -> None:
    config = nested_dict()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_value"]["secret"] = False
    my_generator["script"] = "echo hello > $out/my_value"
    flake = generate_flake(
        temporary_home,
        flake_template=CLAN_CORE / "templates" / "minimal",
        machine_configs=dict(my_machine=config),
    )
    monkeypatch.chdir(flake.path)
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    var_file_path = (
        flake.path / "machines" / "my_machine" / "vars" / "my_generator" / "my_value"
    )
    assert var_file_path.is_file()
    assert var_file_path.read_text() == "hello\n"


@pytest.mark.impure
def test_generate_secret_var_with_default_group(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    sops_setup: SopsSetup,
) -> None:
    user = os.environ.get("USER", "user")
    config = nested_dict()
    config["clan"]["core"]["sops"]["defaultGroups"] = ["my_group"]
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_secret"]["secret"] = True
    my_generator["script"] = "echo hello > $out/my_secret"
    flake = generate_flake(
        temporary_home,
        flake_template=CLAN_CORE / "templates" / "minimal",
        machine_configs=dict(my_machine=config),
    )
    monkeypatch.chdir(flake.path)
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(flake.path),
            user,
            sops_setup.keys[0].pubkey,
        ]
    )
    cli.run(["secrets", "groups", "add-user", "my_group", user])
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    assert not (
        flake.path / "machines" / "my_machine" / "vars" / "my_generator" / "my_secret"
    ).is_file()
    sops_store = SecretStore(Machine(name="my_machine", flake=FlakeId(flake.path)))
    assert sops_store.exists("my_generator", "my_secret")
    assert (
        flake.path
        / "sops"
        / "secrets"
        / "vars-my_machine-my_generator-my_secret"
        / "groups"
        / "my_group"
    ).exists()
    assert sops_store.get("my_generator", "my_secret").decode() == "hello\n"


@pytest.mark.impure
def test_generate_secret_for_multiple_machines(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    sops_setup: SopsSetup,
) -> None:
    user = os.environ.get("USER", "user")
    machine1_config = nested_dict()
    machine1_generator = machine1_config["clan"]["core"]["vars"]["generators"][
        "my_generator"
    ]
    machine1_generator["files"]["my_secret"]["secret"] = True
    machine1_generator["files"]["my_value"]["secret"] = False
    machine1_generator["script"] = (
        "echo machine1 > $out/my_secret && echo machine1 > $out/my_value"
    )
    machine2_config = nested_dict()
    machine2_generator = machine2_config["clan"]["core"]["vars"]["generators"][
        "my_generator"
    ]
    machine2_generator["files"]["my_secret"]["secret"] = True
    machine2_generator["files"]["my_value"]["secret"] = False
    machine2_generator["script"] = (
        "echo machine2 > $out/my_secret && echo machine2 > $out/my_value"
    )
    flake = generate_flake(
        temporary_home,
        flake_template=CLAN_CORE / "templates" / "minimal",
        machine_configs=dict(machine1=machine1_config, machine2=machine2_config),
    )
    monkeypatch.chdir(flake.path)
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(flake.path),
            user,
            sops_setup.keys[0].pubkey,
        ]
    )
    cli.run(["vars", "generate", "--flake", str(flake.path)])
    # check if public vars have been created correctly
    machine1_var_file_path = (
        flake.path / "machines" / "machine1" / "vars" / "my_generator" / "my_value"
    )
    machine2_var_file_path = (
        flake.path / "machines" / "machine2" / "vars" / "my_generator" / "my_value"
    )
    assert machine1_var_file_path.is_file()
    assert machine1_var_file_path.read_text() == "machine1\n"
    assert machine2_var_file_path.is_file()
    assert machine2_var_file_path.read_text() == "machine2\n"
    # check if secret vars have been created correctly
    sops_store1 = SecretStore(Machine(name="machine1", flake=FlakeId(flake.path)))
    sops_store2 = SecretStore(Machine(name="machine2", flake=FlakeId(flake.path)))
    assert sops_store1.exists("my_generator", "my_secret")
    assert sops_store2.exists("my_generator", "my_secret")
    assert sops_store1.get("my_generator", "my_secret").decode() == "machine1\n"
    assert sops_store2.get("my_generator", "my_secret").decode() == "machine2\n"
