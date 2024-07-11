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
    my_generator["files"]["my_secret"]["secret"] = False
    my_generator["script"] = "echo hello > $out/my_secret"
    flake = generate_flake(
        temporary_home,
        flake_template=CLAN_CORE / "templates" / "minimal",
        machine_configs=dict(my_machine=config),
    )
    monkeypatch.chdir(flake.path)
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    secret_path = (
        flake.path / "machines" / "my_machine" / "vars" / "my_generator" / "my_secret"
    )
    assert secret_path.is_file()
    assert secret_path.read_text() == "hello\n"


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
    assert (
        flake.path / "sops" / "secrets" / "vars-my_machine-my_generator-my_secret"
    ).is_dir()
    assert (
        flake.path
        / "sops"
        / "secrets"
        / "vars-my_machine-my_generator-my_secret"
        / "groups"
        / "my_group"
    ).exists()
