import logging
import os
from contextlib import contextmanager
from typing import TYPE_CHECKING, Iterator

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

    cli.run(["secrets", what, "add", "foo", age_keys[0].pubkey, test_flake.name])
    assert (sops_folder / what / "foo" / "key.json").exists()
    with pytest.raises(ClanError):
        cli.run(["secrets", what, "add", "foo", age_keys[0].pubkey, test_flake.name])

    cli.run(
        [
            "secrets",
            what,
            "add",
            "-f",
            "foo",
            age_keys[0].privkey,
            test_flake.name,
        ]
    )

    capsys.readouterr()  # empty the buffer
    cli.run(["secrets", what, "get", "foo", test_flake.name])
    out = capsys.readouterr()  # empty the buffer
    assert age_keys[0].pubkey in out.out

    capsys.readouterr()  # empty the buffer
    cli.run(["secrets", what, "list", test_flake.name])
    out = capsys.readouterr()  # empty the buffer
    assert "foo" in out.out

    cli.run(["secrets", what, "remove", "foo", test_flake.name])
    assert not (sops_folder / what / "foo" / "key.json").exists()

    with pytest.raises(ClanError):  # already removed
        cli.run(["secrets", what, "remove", "foo", test_flake.name])

    capsys.readouterr()
    cli.run(["secrets", what, "list", test_flake.name])
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
    cli.run(["secrets", "groups", "list", test_flake.name])
    assert capsys.readouterr().out == ""

    with pytest.raises(ClanError):  # machine does not exist yet
        cli.run(
            ["secrets", "groups", "add-machine", "group1", "machine1", test_flake.name]
        )
    with pytest.raises(ClanError):  # user does not exist yet
        cli.run(["secrets", "groups", "add-user", "groupb1", "user1", test_flake.name])
    cli.run(
        ["secrets", "machines", "add", "machine1", age_keys[0].pubkey, test_flake.name]
    )
    cli.run(["secrets", "groups", "add-machine", "group1", "machine1", test_flake.name])

    # Should this fail?
    cli.run(["secrets", "groups", "add-machine", "group1", "machine1", test_flake.name])

    cli.run(["secrets", "users", "add", "user1", age_keys[0].pubkey, test_flake.name])
    cli.run(["secrets", "groups", "add-user", "group1", "user1", test_flake.name])

    capsys.readouterr()  # empty the buffer
    cli.run(["secrets", "groups", "list", test_flake.name])
    out = capsys.readouterr().out
    assert "user1" in out
    assert "machine1" in out

    cli.run(["secrets", "groups", "remove-user", "group1", "user1", test_flake.name])
    cli.run(
        ["secrets", "groups", "remove-machine", "group1", "machine1", test_flake.name]
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
    cli.run(["secrets", "list", test_flake.name])
    assert capsys.readouterr().out == ""

    monkeypatch.setenv("SOPS_NIX_SECRET", "foo")
    monkeypatch.setenv("SOPS_AGE_KEY_FILE", str(test_flake.path / ".." / "age.key"))
    cli.run(["secrets", "key", "generate"])
    capsys.readouterr()  # empty the buffer
    cli.run(["secrets", "key", "show"])
    key = capsys.readouterr().out
    assert key.startswith("age1")
    cli.run(["secrets", "users", "add", "testuser", key, test_flake.name])

    with pytest.raises(ClanError):  # does not exist yet
        cli.run(["secrets", "get", "nonexisting", test_flake.name])
    cli.run(["secrets", "set", "initialkey", test_flake.name])
    capsys.readouterr()
    cli.run(["secrets", "get", "initialkey", test_flake.name])
    assert capsys.readouterr().out == "foo"
    capsys.readouterr()
    cli.run(["secrets", "users", "list", test_flake.name])
    users = capsys.readouterr().out.rstrip().split("\n")
    assert len(users) == 1, f"users: {users}"
    owner = users[0]

    monkeypatch.setenv("EDITOR", "cat")
    cli.run(["secrets", "set", "--edit", "initialkey", test_flake.name])
    monkeypatch.delenv("EDITOR")

    cli.run(["secrets", "rename", "initialkey", "key", test_flake.name])

    capsys.readouterr()  # empty the buffer
    cli.run(["secrets", "list", test_flake.name])
    assert capsys.readouterr().out == "key\n"

    cli.run(
        ["secrets", "machines", "add", "machine1", age_keys[0].pubkey, test_flake.name]
    )
    cli.run(["secrets", "machines", "add-secret", "machine1", "key", test_flake.name])
    capsys.readouterr()
    cli.run(["secrets", "machines", "list", test_flake.name])
    assert capsys.readouterr().out == "machine1\n"

    with use_key(age_keys[0].privkey, monkeypatch):
        capsys.readouterr()
        cli.run(["secrets", "get", "key", test_flake.name])

        assert capsys.readouterr().out == "foo"

    cli.run(
        ["secrets", "machines", "remove-secret", "machine1", "key", test_flake.name]
    )

    cli.run(["secrets", "users", "add", "user1", age_keys[1].pubkey, test_flake.name])
    cli.run(["secrets", "users", "add-secret", "user1", "key", test_flake.name])
    capsys.readouterr()
    with use_key(age_keys[1].privkey, monkeypatch):
        cli.run(["secrets", "get", "key", test_flake.name])
    assert capsys.readouterr().out == "foo"
    cli.run(["secrets", "users", "remove-secret", "user1", "key", test_flake.name])

    with pytest.raises(ClanError):  # does not exist yet
        cli.run(
            ["secrets", "groups", "add-secret", "admin-group", "key", test_flake.name]
        )
    cli.run(["secrets", "groups", "add-user", "admin-group", "user1", test_flake.name])
    cli.run(["secrets", "groups", "add-user", "admin-group", owner, test_flake.name])
    cli.run(["secrets", "groups", "add-secret", "admin-group", "key", test_flake.name])

    capsys.readouterr()  # empty the buffer
    cli.run(["secrets", "set", "--group", "admin-group", "key2", test_flake.name])

    with use_key(age_keys[1].privkey, monkeypatch):
        capsys.readouterr()
        cli.run(["secrets", "get", "key", test_flake.name])
        assert capsys.readouterr().out == "foo"

    # extend group will update secrets
    cli.run(["secrets", "users", "add", "user2", age_keys[2].pubkey, test_flake.name])
    cli.run(["secrets", "groups", "add-user", "admin-group", "user2", test_flake.name])

    with use_key(age_keys[2].privkey, monkeypatch):  # user2
        capsys.readouterr()
        cli.run(["secrets", "get", "key", test_flake.name])
        assert capsys.readouterr().out == "foo"

    cli.run(
        ["secrets", "groups", "remove-user", "admin-group", "user2", test_flake.name]
    )
    with pytest.raises(ClanError), use_key(age_keys[2].privkey, monkeypatch):
        # user2 is not in the group anymore
        capsys.readouterr()
        cli.run(["secrets", "get", "key", test_flake.name])
        print(capsys.readouterr().out)

    cli.run(
        ["secrets", "groups", "remove-secret", "admin-group", "key", test_flake.name]
    )

    cli.run(["secrets", "remove", "key", test_flake.name])
    cli.run(["secrets", "remove", "key2", test_flake.name])

    capsys.readouterr()  # empty the buffer
    cli.run(["secrets", "list", test_flake.name])
    assert capsys.readouterr().out == ""
