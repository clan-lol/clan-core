import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

import pytest
from cli import Cli
from fixtures_flakes import FlakeForTest

from clan_cli.errors import ClanError

if TYPE_CHECKING:
    from age_keys import KeyPair

log = logging.getLogger(__name__)


def _test_identities(
    what: str,
    test_flake: FlakeForTest,
    capsys: pytest.CaptureFixture,
    age_keys: list["KeyPair"],
) -> None:
    cli = Cli()
    sops_folder = test_flake.path / "sops"

    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            what,
            "add",
            "foo",
            age_keys[0].pubkey,
        ]
    )
    assert (sops_folder / what / "foo" / "key.json").exists()
    with pytest.raises(ClanError):
        cli.run(["secrets", what, "add", "foo", age_keys[0].pubkey])

    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            what,
            "add",
            "-f",
            "foo",
            age_keys[0].privkey,
        ]
    )

    capsys.readouterr()  # empty the buffer
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            what,
            "get",
            "foo",
        ]
    )
    out = capsys.readouterr()  # empty the buffer
    assert age_keys[0].pubkey in out.out

    capsys.readouterr()  # empty the buffer
    cli.run(["--flake", str(test_flake.path), "secrets", what, "list"])
    out = capsys.readouterr()  # empty the buffer
    assert "foo" in out.out

    cli.run(["--flake", str(test_flake.path), "secrets", what, "remove", "foo"])
    assert not (sops_folder / what / "foo" / "key.json").exists()

    with pytest.raises(ClanError):  # already removed
        cli.run(["--flake", str(test_flake.path), "secrets", what, "remove", "foo"])

    capsys.readouterr()
    cli.run(["--flake", str(test_flake.path), "secrets", what, "list"])
    out = capsys.readouterr()
    assert "foo" not in out.out


def test_users(
    test_flake: FlakeForTest, capsys: pytest.CaptureFixture, age_keys: list["KeyPair"]
) -> None:
    _test_identities("users", test_flake, capsys, age_keys)


def test_machines(
    test_flake: FlakeForTest, capsys: pytest.CaptureFixture, age_keys: list["KeyPair"]
) -> None:
    _test_identities("machines", test_flake, capsys, age_keys)


def test_groups(
    test_flake: FlakeForTest, capsys: pytest.CaptureFixture, age_keys: list["KeyPair"]
) -> None:
    cli = Cli()
    capsys.readouterr()  # empty the buffer
    cli.run(["--flake", str(test_flake.path), "secrets", "groups", "list"])
    assert capsys.readouterr().out == ""

    with pytest.raises(ClanError):  # machine does not exist yet
        cli.run(
            [
                "--flake",
                str(test_flake.path),
                "secrets",
                "groups",
                "add-machine",
                "group1",
                "machine1",
            ]
        )
    with pytest.raises(ClanError):  # user does not exist yet
        cli.run(
            [
                "--flake",
                str(test_flake.path),
                "secrets",
                "groups",
                "add-user",
                "groupb1",
                "user1",
            ]
        )
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "machines",
            "add",
            "machine1",
            age_keys[0].pubkey,
        ]
    )
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "groups",
            "add-machine",
            "group1",
            "machine1",
        ]
    )

    # Should this fail?
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "groups",
            "add-machine",
            "group1",
            "machine1",
        ]
    )

    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "users",
            "add",
            "user1",
            age_keys[0].pubkey,
        ]
    )
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "groups",
            "add-user",
            "group1",
            "user1",
        ]
    )

    capsys.readouterr()  # empty the buffer
    cli.run(["--flake", str(test_flake.path), "secrets", "groups", "list"])
    out = capsys.readouterr().out
    assert "user1" in out
    assert "machine1" in out

    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "groups",
            "remove-user",
            "group1",
            "user1",
        ]
    )
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "groups",
            "remove-machine",
            "group1",
            "machine1",
        ]
    )
    groups = os.listdir(test_flake.path / "sops" / "groups")
    assert len(groups) == 0


@contextmanager
def use_key(key: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    old_key = os.environ["SOPS_AGE_KEY_FILE"]
    monkeypatch.delenv("SOPS_AGE_KEY_FILE")
    monkeypatch.setenv("SOPS_AGE_KEY", key)
    try:
        yield
    finally:
        monkeypatch.delenv("SOPS_AGE_KEY")
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", old_key)


def test_secrets(
    test_flake: FlakeForTest,
    capsys: pytest.CaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    age_keys: list["KeyPair"],
) -> None:
    cli = Cli()
    capsys.readouterr()  # empty the buffer
    cli.run(["--flake", str(test_flake.path), "secrets", "list"])
    assert capsys.readouterr().out == ""

    monkeypatch.setenv("SOPS_NIX_SECRET", "foo")
    monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(test_flake.path / ".." / "age.key"))
    cli.run(["--flake", str(test_flake.path), "secrets", "key", "generate"])
    capsys.readouterr()  # empty the buffer
    cli.run(["--flake", str(test_flake.path), "secrets", "key", "show"])
    key = capsys.readouterr().out
    assert key.startswith("age1")
    cli.run(
        ["--flake", str(test_flake.path), "secrets", "users", "add", "testuser", key]
    )

    with pytest.raises(ClanError):  # does not exist yet
        cli.run(["--flake", str(test_flake.path), "secrets", "get", "nonexisting"])
    cli.run(["--flake", str(test_flake.path), "secrets", "set", "initialkey"])
    capsys.readouterr()
    cli.run(["--flake", str(test_flake.path), "secrets", "get", "initialkey"])
    assert capsys.readouterr().out == "foo"
    capsys.readouterr()
    cli.run(["--flake", str(test_flake.path), "secrets", "users", "list"])
    users = capsys.readouterr().out.rstrip().split("\n")
    assert len(users) == 1, f"users: {users}"
    owner = users[0]

    monkeypatch.setenv("EDITOR", "cat")
    cli.run(["--flake", str(test_flake.path), "secrets", "set", "--edit", "initialkey"])
    monkeypatch.delenv("EDITOR")

    cli.run(["--flake", str(test_flake.path), "secrets", "rename", "initialkey", "key"])

    capsys.readouterr()  # empty the buffer
    cli.run(["--flake", str(test_flake.path), "secrets", "list"])
    assert capsys.readouterr().out == "key\n"

    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "machines",
            "add",
            "machine1",
            age_keys[0].pubkey,
        ]
    )
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "machines",
            "add-secret",
            "machine1",
            "key",
        ]
    )
    capsys.readouterr()
    cli.run(["--flake", str(test_flake.path), "secrets", "machines", "list"])
    assert capsys.readouterr().out == "machine1\n"

    with use_key(age_keys[0].privkey, monkeypatch):
        capsys.readouterr()
        cli.run(["--flake", str(test_flake.path), "secrets", "get", "key"])

        assert capsys.readouterr().out == "foo"

    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "machines",
            "remove-secret",
            "machine1",
            "key",
        ]
    )

    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "users",
            "add",
            "user1",
            age_keys[1].pubkey,
        ]
    )
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "users",
            "add-secret",
            "user1",
            "key",
        ]
    )
    capsys.readouterr()
    with use_key(age_keys[1].privkey, monkeypatch):
        cli.run(["--flake", str(test_flake.path), "secrets", "get", "key"])
    assert capsys.readouterr().out == "foo"
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "users",
            "remove-secret",
            "user1",
            "key",
        ]
    )

    with pytest.raises(ClanError):  # does not exist yet
        cli.run(
            [
                "--flake",
                str(test_flake.path),
                "secrets",
                "groups",
                "add-secret",
                "admin-group",
                "key",
            ]
        )
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "groups",
            "add-user",
            "admin-group",
            "user1",
        ]
    )
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "groups",
            "add-user",
            "admin-group",
            owner,
        ]
    )
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "groups",
            "add-secret",
            "admin-group",
            "key",
        ]
    )

    capsys.readouterr()  # empty the buffer
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "set",
            "--group",
            "admin-group",
            "key2",
        ]
    )

    with use_key(age_keys[1].privkey, monkeypatch):
        capsys.readouterr()
        cli.run(["--flake", str(test_flake.path), "secrets", "get", "key"])
        assert capsys.readouterr().out == "foo"

    # extend group will update secrets
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "users",
            "add",
            "user2",
            age_keys[2].pubkey,
        ]
    )
    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "groups",
            "add-user",
            "admin-group",
            "user2",
        ]
    )

    with use_key(age_keys[2].privkey, monkeypatch):  # user2
        capsys.readouterr()
        cli.run(["--flake", str(test_flake.path), "secrets", "get", "key"])
        assert capsys.readouterr().out == "foo"

    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "groups",
            "remove-user",
            "admin-group",
            "user2",
        ]
    )
    with pytest.raises(ClanError), use_key(age_keys[2].privkey, monkeypatch):
        # user2 is not in the group anymore
        capsys.readouterr()
        cli.run(["--flake", str(test_flake.path), "secrets", "get", "key"])
        print(capsys.readouterr().out)

    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "secrets",
            "groups",
            "remove-secret",
            "admin-group",
            "key",
        ]
    )

    cli.run(["--flake", str(test_flake.path), "secrets", "remove", "key"])
    cli.run(["--flake", str(test_flake.path), "secrets", "remove", "key2"])

    capsys.readouterr()  # empty the buffer
    cli.run(["--flake", str(test_flake.path), "secrets", "list"])
    assert capsys.readouterr().out == ""
