"""Tests for CLI operations respecting the clan.directory setting.

These tests verify that secrets and vars operations correctly use
the custom directory path when clan.directory is configured.
"""

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest
from clan_cli.secrets.secrets import list_secrets
from clan_cli.secrets.users import list_users
from clan_cli.tests.age_keys import KeyPair, SopsSetup
from clan_cli.tests.helpers import cli

from clan_lib.api.directory import get_clan_dir
from clan_lib.flake import Flake

CLAN_NIX_WITH_DIRECTORY = """
{
  directory = ./clan;
  meta.name = "test-directory-settings";
}
"""


def init_git(flake_path: Path) -> None:
    """Initialize git repo for the flake."""
    subprocess.run(["git", "init", "-b", "main"], cwd=flake_path, check=True)
    subprocess.run(["git", "add", "."], cwd=flake_path, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=test",
            "-c",
            "user.email=test@test.com",
            "commit",
            "-m",
            "Initial commit",
        ],
        cwd=flake_path,
        check=True,
    )


@pytest.mark.with_core
def test_vars_keygen_with_directory_setting(
    clan_flake: Callable[..., Flake],
    sops_setup: SopsSetup,
) -> None:
    """Test that vars keygen creates admin user in the custom directory."""
    flake = clan_flake(raw=CLAN_NIX_WITH_DIRECTORY)
    clan_dir = flake.path / "clan"
    clan_dir.mkdir(exist_ok=True)

    init_git(flake.path)
    sops_setup.init(flake.path)

    assert (clan_dir / "sops" / "users" / "admin" / "key.json").exists(), (
        "Admin user should be in clan/sops/users/"
    )
    assert not (flake.path / "sops" / "users" / "admin").exists(), (
        "Admin user should NOT be in sops/users/ (flake root)"
    )


@pytest.mark.with_core
def test_secrets_users_with_directory_setting(
    clan_flake: Callable[..., Flake],
    sops_setup: SopsSetup,
    age_keys: list[KeyPair],
) -> None:
    """Test that secrets users add creates keys in the custom directory."""
    flake = clan_flake(raw=CLAN_NIX_WITH_DIRECTORY)
    clan_dir = flake.path / "clan"
    clan_dir.mkdir(exist_ok=True)

    init_git(flake.path)
    sops_setup.init(flake.path)

    # Add a user
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(flake.path),
            "testuser",
            age_keys[1].pubkey,
        ],
    )

    assert (clan_dir / "sops" / "users" / "testuser" / "key.json").exists(), (
        "Key should be in clan/sops/users/"
    )
    assert not (flake.path / "sops" / "users" / "testuser").exists(), (
        "Key should NOT be in sops/users/ (flake root)"
    )


@pytest.mark.with_core
def test_secrets_users_list_with_directory_setting(
    clan_flake: Callable[..., Flake],
    sops_setup: SopsSetup,
    age_keys: list[KeyPair],
) -> None:
    """Test that secrets users list finds users in the custom directory."""
    flake = clan_flake(raw=CLAN_NIX_WITH_DIRECTORY)
    clan_dir = flake.path / "clan"
    clan_dir.mkdir(exist_ok=True)

    init_git(flake.path)
    sops_setup.init(flake.path)

    # Add users
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(flake.path),
            "alice",
            age_keys[1].pubkey,
        ],
    )
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(flake.path),
            "bob",
            age_keys[2].pubkey,
        ],
    )

    users = list_users(get_clan_dir(flake))
    assert "alice" in users, "list_users should find alice in clan/sops/users/"
    assert "bob" in users, "list_users should find bob in clan/sops/users/"


@pytest.mark.with_core
def test_secrets_machines_with_directory_setting(
    clan_flake: Callable[..., Flake],
    sops_setup: SopsSetup,
    age_keys: list[KeyPair],
) -> None:
    """Test that secrets machines add creates keys in the custom directory."""
    flake = clan_flake(raw=CLAN_NIX_WITH_DIRECTORY)
    clan_dir = flake.path / "clan"
    clan_dir.mkdir(exist_ok=True)

    init_git(flake.path)
    sops_setup.init(flake.path)

    # Add a machine
    cli.run(
        [
            "secrets",
            "machines",
            "add",
            "--flake",
            str(flake.path),
            "testmachine",
            age_keys[1].pubkey,
        ],
    )

    assert (clan_dir / "sops" / "machines" / "testmachine" / "key.json").exists(), (
        "Key should be in clan/sops/machines/"
    )
    assert not (flake.path / "sops" / "machines" / "testmachine").exists(), (
        "Key should NOT be in sops/machines/ (flake root)"
    )


@pytest.mark.with_core
def test_secrets_set_with_directory_setting(
    clan_flake: Callable[..., Flake],
    sops_setup: SopsSetup,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that secrets set creates files in the custom directory."""
    flake = clan_flake(raw=CLAN_NIX_WITH_DIRECTORY)
    clan_dir = flake.path / "clan"
    clan_dir.mkdir(exist_ok=True)

    init_git(flake.path)
    sops_setup.init(flake.path)

    # Set a secret
    monkeypatch.setenv("SOPS_NIX_SECRET", "my-secret-value")
    cli.run(
        [
            "secrets",
            "set",
            "--flake",
            str(flake.path),
            "my-secret",
        ],
    )

    assert (clan_dir / "sops" / "secrets" / "my-secret" / "secret").exists(), (
        "Secret should be in clan/sops/secrets/"
    )
    assert not (flake.path / "sops" / "secrets" / "my-secret").exists(), (
        "Secret should NOT be in sops/secrets/ (flake root)"
    )


@pytest.mark.with_core
def test_secrets_list_with_directory_setting(
    clan_flake: Callable[..., Flake],
    sops_setup: SopsSetup,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that secrets list finds secrets in the custom directory."""
    flake = clan_flake(raw=CLAN_NIX_WITH_DIRECTORY)
    clan_dir = flake.path / "clan"
    clan_dir.mkdir(exist_ok=True)

    init_git(flake.path)
    sops_setup.init(flake.path)

    # Set secrets
    monkeypatch.setenv("SOPS_NIX_SECRET", "value1")
    cli.run(["secrets", "set", "--flake", str(flake.path), "secret1"])

    monkeypatch.setenv("SOPS_NIX_SECRET", "value2")
    cli.run(["secrets", "set", "--flake", str(flake.path), "secret2"])

    secrets = list_secrets(get_clan_dir(flake))
    assert "secret1" in secrets, (
        "list_secrets should find secret1 in clan/sops/secrets/"
    )
    assert "secret2" in secrets, (
        "list_secrets should find secret2 in clan/sops/secrets/"
    )


@pytest.mark.with_core
def test_secrets_groups_with_directory_setting(
    clan_flake: Callable[..., Flake],
    sops_setup: SopsSetup,
    age_keys: list[KeyPair],
) -> None:
    """Test that secrets groups operations work with the custom directory."""
    flake = clan_flake(raw=CLAN_NIX_WITH_DIRECTORY)
    clan_dir = flake.path / "clan"
    clan_dir.mkdir(exist_ok=True)

    init_git(flake.path)
    sops_setup.init(flake.path)

    # Add a user first
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(flake.path),
            "groupuser",
            age_keys[1].pubkey,
        ],
    )

    # Add user to a group
    cli.run(
        [
            "secrets",
            "groups",
            "add-user",
            "--flake",
            str(flake.path),
            "mygroup",
            "groupuser",
        ],
    )

    assert (
        clan_dir / "sops" / "groups" / "mygroup" / "users" / "groupuser"
    ).exists(), "Group should be in clan/sops/groups/"
    assert not (flake.path / "sops" / "groups" / "mygroup").exists(), (
        "Group should NOT be in sops/groups/ (flake root)"
    )


@pytest.mark.with_core
def test_secrets_remove_with_directory_setting(
    clan_flake: Callable[..., Flake],
    sops_setup: SopsSetup,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that secrets remove works with the custom directory."""
    flake = clan_flake(raw=CLAN_NIX_WITH_DIRECTORY)
    clan_dir = flake.path / "clan"
    clan_dir.mkdir(exist_ok=True)

    init_git(flake.path)
    sops_setup.init(flake.path)

    # Set a secret
    monkeypatch.setenv("SOPS_NIX_SECRET", "to-be-removed")
    cli.run(["secrets", "set", "--flake", str(flake.path), "temp-secret"])

    assert (clan_dir / "sops" / "secrets" / "temp-secret" / "secret").exists(), (
        "Secret should exist in clan/sops/secrets/ before removal"
    )

    cli.run(["secrets", "remove", "--flake", str(flake.path), "temp-secret"])

    assert not (clan_dir / "sops" / "secrets" / "temp-secret").exists(), (
        "Secret should be removed from clan/sops/secrets/"
    )


@pytest.mark.with_core
def test_secrets_key_generate_with_directory_setting(
    clan_flake: Callable[..., Flake],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that secrets key generate works with the custom directory."""
    flake = clan_flake(raw=CLAN_NIX_WITH_DIRECTORY)
    clan_dir = flake.path / "clan"
    clan_dir.mkdir(exist_ok=True)

    init_git(flake.path)

    # Set up a key file location
    key_file = tmp_path / "age.key"
    monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(key_file))

    cli.run(["secrets", "key", "generate", "--flake", str(flake.path)])

    assert key_file.exists(), "Age key file should be created"


CLAN_NIX_WITH_DIRECTORY_AND_MACHINE = """
{
  directory = ./clan;
  meta.name = "test-directory-settings";

  inventory.machines.my_machine = {};

  machines.my_machine = { ... }: {
    nixpkgs.hostPlatform = "x86_64-linux";
    clan.core.settings.state-version.enable = false;
    clan.core.vars.generators.my_generator = {
      files.my_secret.secret = true;
      files.my_public.secret = false;
      script = "echo secret_value > $out/my_secret; echo public_value > $out/my_public";
    };
  };
}
"""


@pytest.mark.with_core
def test_vars_generate_with_directory_setting(
    clan_flake: Callable[..., Flake],
    sops_setup: SopsSetup,
) -> None:
    """Test that vars generate creates files in the custom directory."""
    flake = clan_flake(raw=CLAN_NIX_WITH_DIRECTORY_AND_MACHINE)
    clan_dir = flake.path / "clan"
    clan_dir.mkdir(exist_ok=True)

    init_git(flake.path)
    sops_setup.init(flake.path)

    cli.run(["vars", "generate", "--flake", str(flake.path), "my_machine"])

    public_var_path = (
        clan_dir
        / "vars"
        / "per-machine"
        / "my_machine"
        / "my_generator"
        / "my_public"
        / "value"
    )
    assert public_var_path.exists(), (
        f"Public var should be in clan/vars/, not found at {public_var_path}"
    )
    assert public_var_path.read_text().strip() == "public_value", (
        "Public var should contain 'public_value'"
    )
    assert not (flake.path / "vars" / "per-machine" / "my_machine").exists(), (
        "Vars should NOT be in vars/ (flake root)"
    )

    secret_path = (
        clan_dir
        / "vars"
        / "per-machine"
        / "my_machine"
        / "my_generator"
        / "my_secret"
        / "secret"
    )
    assert secret_path.exists(), (
        f"Secret var should be in clan/vars/, not found at {secret_path}"
    )
