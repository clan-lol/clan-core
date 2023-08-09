import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from environment import mock_env
from secret_cli import SecretCli

from clan_cli.errors import ClanError

if TYPE_CHECKING:
    from test_keys import KeyPair


def _test_identities(
    what: str,
    clan_flake: Path,
    capsys: pytest.CaptureFixture,
    test_keys: list["KeyPair"],
) -> None:
    cli = SecretCli()
    sops_folder = clan_flake / "sops"

    cli.run([what, "add", "foo", test_keys[0].pubkey])
    assert (sops_folder / what / "foo" / "key.json").exists()
    with pytest.raises(ClanError):
        cli.run([what, "add", "foo", test_keys[0].pubkey])

    cli.run(
        [
            what,
            "add",
            "-f",
            "foo",
            test_keys[0].privkey,
        ]
    )
    capsys.readouterr()  # empty the buffer

    cli.run([what, "list"])
    out = capsys.readouterr()  # empty the buffer
    assert "foo" in out.out

    cli.run([what, "remove", "foo"])
    assert not (sops_folder / what / "foo" / "key.json").exists()

    with pytest.raises(ClanError):  # already removed
        cli.run([what, "remove", "foo"])

    capsys.readouterr()
    cli.run([what, "list"])
    out = capsys.readouterr()
    assert "foo" not in out.out


def test_users(
    clan_flake: Path, capsys: pytest.CaptureFixture, test_keys: list["KeyPair"]
) -> None:
    _test_identities("users", clan_flake, capsys, test_keys)


def test_machines(
    clan_flake: Path, capsys: pytest.CaptureFixture, test_keys: list["KeyPair"]
) -> None:
    _test_identities("machines", clan_flake, capsys, test_keys)


def test_groups(
    clan_flake: Path, capsys: pytest.CaptureFixture, test_keys: list["KeyPair"]
) -> None:
    cli = SecretCli()
    capsys.readouterr()  # empty the buffer
    cli.run(["groups", "list"])
    assert capsys.readouterr().out == ""

    with pytest.raises(ClanError):  # machine does not exist yet
        cli.run(["groups", "add-machine", "group1", "machine1"])
    with pytest.raises(ClanError):  # user does not exist yet
        cli.run(["groups", "add-user", "groupb1", "user1"])
    cli.run(["machines", "add", "machine1", test_keys[0].pubkey])
    cli.run(["groups", "add-machine", "group1", "machine1"])

    # Should this fail?
    cli.run(["groups", "add-machine", "group1", "machine1"])

    cli.run(["users", "add", "user1", test_keys[0].pubkey])
    cli.run(["groups", "add-user", "group1", "user1"])

    capsys.readouterr()  # empty the buffer
    cli.run(["groups", "list"])
    out = capsys.readouterr().out
    assert "user1" in out
    assert "machine1" in out

    cli.run(["groups", "remove-user", "group1", "user1"])
    cli.run(["groups", "remove-machine", "group1", "machine1"])
    groups = os.listdir(clan_flake / "sops" / "groups")
    assert len(groups) == 0


def test_secrets(
    clan_flake: Path, capsys: pytest.CaptureFixture, test_keys: list["KeyPair"]
) -> None:
    cli = SecretCli()
    capsys.readouterr()  # empty the buffer
    cli.run(["list"])
    assert capsys.readouterr().out == ""

    with mock_env(
        SOPS_NIX_SECRET="foo", SOPS_AGE_KEY_FILE=str(clan_flake / ".." / "age.key")
    ):
        with pytest.raises(ClanError):  # does not exist yet
            cli.run(["get", "nonexisting"])
        cli.run(["set", "key"])
        capsys.readouterr()
        cli.run(["get", "key"])
        assert capsys.readouterr().out == "foo"
        capsys.readouterr()
        cli.run(["users", "list"])
        users = capsys.readouterr().out.rstrip().split("\n")
        assert len(users) == 1, f"users: {users}"
        owner = users[0]

        capsys.readouterr()  # empty the buffer
        cli.run(["list"])
        assert capsys.readouterr().out == "key\n"

        cli.run(["machines", "add", "machine1", test_keys[0].pubkey])
        cli.run(["machines", "add-secret", "machine1", "key"])

        with mock_env(SOPS_AGE_KEY=test_keys[0].privkey, SOPS_AGE_KEY_FILE=""):
            capsys.readouterr()
            cli.run(["get", "key"])
            assert capsys.readouterr().out == "foo"
        cli.run(["machines", "remove-secret", "machine1", "key"])

        cli.run(["users", "add", "user1", test_keys[1].pubkey])
        cli.run(["users", "add-secret", "user1", "key"])
        with mock_env(SOPS_AGE_KEY=test_keys[1].privkey, SOPS_AGE_KEY_FILE=""):
            capsys.readouterr()
            cli.run(["get", "key"])
            assert capsys.readouterr().out == "foo"
        cli.run(["users", "remove-secret", "user1", "key"])

        with pytest.raises(ClanError):  # does not exist yet
            cli.run(["groups", "add-secret", "admin-group", "key"])
        cli.run(["groups", "add-user", "admin-group", "user1"])
        cli.run(["groups", "add-user", "admin-group", owner])
        cli.run(["groups", "add-secret", "admin-group", "key"])

        capsys.readouterr()  # empty the buffer
        cli.run(["set", "--group", "admin-group", "key2"])

        with mock_env(SOPS_AGE_KEY=test_keys[1].privkey, SOPS_AGE_KEY_FILE=""):
            capsys.readouterr()
            cli.run(["get", "key"])
            assert capsys.readouterr().out == "foo"
        cli.run(["groups", "remove-secret", "admin-group", "key"])

    cli.run(["remove", "key"])
    cli.run(["remove", "key2"])

    capsys.readouterr()  # empty the buffer
    cli.run(["list"])
    assert capsys.readouterr().out == ""
