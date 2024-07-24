import os
import subprocess
from collections import defaultdict
from collections.abc import Callable
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest
from age_keys import SopsSetup
from fixtures_flakes import generate_flake
from helpers import cli
from root import CLAN_CORE

from clan_cli.clan_uri import FlakeId
from clan_cli.machines.machines import Machine
from clan_cli.nix import nix_shell
from clan_cli.vars.secret_modules import password_store, sops


def def_value() -> defaultdict:
    return defaultdict(def_value)


# allows defining nested dictionary in a single line
nested_dict: Callable[[], dict[str, Any]] = lambda: defaultdict(def_value)


def test_get_subgraph() -> None:
    from clan_cli.vars.generate import _get_subgraph

    graph = dict(
        a={"b", "c"},
        b={"c"},
        c=set(),
        d=set(),
    )
    assert _get_subgraph(graph, "a") == {
        "a": {"b", "c"},
        "b": {"c"},
        "c": set(),
    }
    assert _get_subgraph(graph, "b") == {"b": {"c"}, "c": set()}


def test_dependencies_as_files() -> None:
    from clan_cli.vars.generate import dependencies_as_dir

    decrypted_dependencies = dict(
        gen_1=dict(
            var_1a=b"var_1a",
            var_1b=b"var_1b",
        ),
        gen_2=dict(
            var_2a=b"var_2a",
            var_2b=b"var_2b",
        ),
    )
    with TemporaryDirectory() as tmpdir:
        dep_tmpdir = Path(tmpdir)
        dependencies_as_dir(decrypted_dependencies, dep_tmpdir)
        assert dep_tmpdir.is_dir()
        assert (dep_tmpdir / "gen_1" / "var_1a").read_bytes() == b"var_1a"
        assert (dep_tmpdir / "gen_1" / "var_1b").read_bytes() == b"var_1b"
        assert (dep_tmpdir / "gen_2" / "var_2a").read_bytes() == b"var_2a"
        assert (dep_tmpdir / "gen_2" / "var_2b").read_bytes() == b"var_2b"
        # ensure the files are not world readable
        assert (dep_tmpdir / "gen_1" / "var_1a").stat().st_mode & 0o777 == 0o600
        assert (dep_tmpdir / "gen_1" / "var_1b").stat().st_mode & 0o777 == 0o600
        assert (dep_tmpdir / "gen_2" / "var_2a").stat().st_mode & 0o777 == 0o600
        assert (dep_tmpdir / "gen_2" / "var_2b").stat().st_mode & 0o777 == 0o600


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
def test_generate_secret_var_sops(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    sops_setup: SopsSetup,
) -> None:
    user = os.environ.get("USER", "user")
    config = nested_dict()
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
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    var_file_path = (
        flake.path / "machines" / "my_machine" / "vars" / "my_generator" / "my_secret"
    )
    assert not var_file_path.is_file()
    sops_store = sops.SecretStore(Machine(name="my_machine", flake=FlakeId(flake.path)))
    assert sops_store.exists("my_generator", "my_secret")
    assert sops_store.get("my_generator", "my_secret").decode() == "hello\n"


@pytest.mark.impure
def test_generate_secret_var_sops_with_default_group(
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
    sops_store = sops.SecretStore(Machine(name="my_machine", flake=FlakeId(flake.path)))
    assert sops_store.exists("my_generator", "my_secret")
    assert (
        flake.path
        / "sops"
        / "vars"
        / "my_machine"
        / "my_generator"
        / "my_secret"
        / "groups"
        / "my_group"
    ).exists()
    assert sops_store.get("my_generator", "my_secret").decode() == "hello\n"


@pytest.mark.impure
def test_generate_secret_var_password_store(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
) -> None:
    config = nested_dict()
    my_generator = config["clan"]["core"]["vars"]["settings"]["secretStore"] = (
        "password-store"
    )
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_secret"]["secret"] = True
    my_generator["script"] = "echo hello > $out/my_secret"
    flake = generate_flake(
        temporary_home,
        flake_template=CLAN_CORE / "templates" / "minimal",
        machine_configs=dict(my_machine=config),
    )
    monkeypatch.chdir(flake.path)
    gnupghome = temporary_home / "gpg"
    gnupghome.mkdir(mode=0o700)
    monkeypatch.setenv("GNUPGHOME", str(gnupghome))
    monkeypatch.setenv("PASSWORD_STORE_DIR", str(temporary_home / "pass"))
    gpg_key_spec = temporary_home / "gpg_key_spec"
    gpg_key_spec.write_text(
        """
        Key-Type: 1
        Key-Length: 1024
        Name-Real: Root Superuser
        Name-Email: test@local
        Expire-Date: 0
        %no-protection
    """
    )
    subprocess.run(
        nix_shell(
            ["nixpkgs#gnupg"], ["gpg", "--batch", "--gen-key", str(gpg_key_spec)]
        ),
        check=True,
    )
    subprocess.run(
        nix_shell(["nixpkgs#pass"], ["pass", "init", "test@local"]), check=True
    )
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    var_file_path = (
        flake.path / "machines" / "my_machine" / "vars" / "my_generator" / "my_secret"
    )
    assert not var_file_path.is_file()
    store = password_store.SecretStore(
        Machine(name="my_machine", flake=FlakeId(flake.path))
    )
    assert store.exists("my_generator", "my_secret")
    assert store.get("my_generator", "my_secret").decode() == "hello\n"


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
    sops_store1 = sops.SecretStore(Machine(name="machine1", flake=FlakeId(flake.path)))
    sops_store2 = sops.SecretStore(Machine(name="machine2", flake=FlakeId(flake.path)))
    assert sops_store1.exists("my_generator", "my_secret")
    assert sops_store2.exists("my_generator", "my_secret")
    assert sops_store1.get("my_generator", "my_secret").decode() == "machine1\n"
    assert sops_store2.get("my_generator", "my_secret").decode() == "machine2\n"


@pytest.mark.impure
def test_dependant_generators(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
) -> None:
    config = nested_dict()
    parent_gen = config["clan"]["core"]["vars"]["generators"]["parent_generator"]
    parent_gen["files"]["my_value"]["secret"] = False
    parent_gen["script"] = "echo hello > $out/my_value"
    child_gen = config["clan"]["core"]["vars"]["generators"]["child_generator"]
    child_gen["files"]["my_value"]["secret"] = False
    child_gen["dependencies"] = ["parent_generator"]
    child_gen["script"] = "cat $in/parent_generator/my_value > $out/my_value"
    flake = generate_flake(
        temporary_home,
        flake_template=CLAN_CORE / "templates" / "minimal",
        machine_configs=dict(my_machine=config),
    )
    monkeypatch.chdir(flake.path)
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    parent_file_path = (
        flake.path / "machines" / "my_machine" / "vars" / "child_generator" / "my_value"
    )
    assert parent_file_path.is_file()
    assert parent_file_path.read_text() == "hello\n"
    child_file_path = (
        flake.path / "machines" / "my_machine" / "vars" / "child_generator" / "my_value"
    )
    assert child_file_path.is_file()
    assert child_file_path.read_text() == "hello\n"


@pytest.mark.impure
@pytest.mark.parametrize(
    ("prompt_type", "input_value"),
    [
        ("line", "my input"),
        ("multiline", "my\nmultiline\ninput\n"),
        # The hidden type cannot easily be tested, as getpass() reads from /dev/tty directly
        # ("hidden", "my hidden input"),
    ],
)
def test_prompt(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    prompt_type: str,
    input_value: str,
) -> None:
    config = nested_dict()
    my_generator = config["clan"]["core"]["vars"]["generators"]["my_generator"]
    my_generator["files"]["my_value"]["secret"] = False
    my_generator["prompts"]["prompt1"]["description"] = "dream2nix"
    my_generator["prompts"]["prompt1"]["type"] = prompt_type
    my_generator["script"] = "cat $prompts/prompt1 > $out/my_value"
    flake = generate_flake(
        temporary_home,
        flake_template=CLAN_CORE / "templates" / "minimal",
        machine_configs=dict(my_machine=config),
    )
    monkeypatch.chdir(flake.path)
    monkeypatch.setattr("sys.stdin", StringIO(input_value))
    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])
    var_file_path = (
        flake.path / "machines" / "my_machine" / "vars" / "my_generator" / "my_value"
    )
    assert var_file_path.is_file()
    assert var_file_path.read_text() == input_value
