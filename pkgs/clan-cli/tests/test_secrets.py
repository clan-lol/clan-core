import argparse
import os
from pathlib import Path

import pytest
from environment import mock_env

from clan_cli.errors import ClanError
from clan_cli.secrets import register_parser


class SecretCli:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser()
        register_parser(self.parser)

    def run(self, args: list[str]) -> argparse.Namespace:
        parsed = self.parser.parse_args(args)
        parsed.func(parsed)
        return parsed


PUBKEY = "age1dhwqzkah943xzc34tc3dlmfayyevcmdmxzjezdgdy33euxwf59vsp3vk3c"
PRIVKEY = "AGE-SECRET-KEY-1KF8E3SR3TTGL6M476SKF7EEMR4H9NF7ZWYSLJUAK8JX276JC7KUSSURKFK"

PUBKEY_2 = "age14tva0txcrl0zes05x7gkx56qd6wd9q3nwecjac74xxzz4l47r44sv3fz62"
PRIVKEY_2 = "AGE-SECRET-KEY-1U5ENXZQAY62NC78Y2WC0SEGRRMAEEKH79EYY5TH4GPFWJKEAY0USZ6X7YQ"


def _test_identities(
    what: str, clan_flake: Path, capsys: pytest.CaptureFixture
) -> None:
    cli = SecretCli()
    sops_folder = clan_flake / "sops"

    cli.run([what, "add", "foo", PUBKEY])
    assert (sops_folder / what / "foo" / "key.json").exists()
    with pytest.raises(ClanError):
        cli.run([what, "add", "foo", PUBKEY])

    cli.run(
        [
            what,
            "add",
            "-f",
            "foo",
            PRIVKEY,
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


def test_users(clan_flake: Path, capsys: pytest.CaptureFixture) -> None:
    _test_identities("users", clan_flake, capsys)


def test_machines(clan_flake: Path, capsys: pytest.CaptureFixture) -> None:
    _test_identities("machines", clan_flake, capsys)


def test_groups(clan_flake: Path, capsys: pytest.CaptureFixture) -> None:
    cli = SecretCli()
    capsys.readouterr()  # empty the buffer
    cli.run(["groups", "list"])
    assert capsys.readouterr().out == ""

    with pytest.raises(ClanError):  # machine does not exist yet
        cli.run(["groups", "add-machine", "group1", "machine1"])
    with pytest.raises(ClanError):  # user does not exist yet
        cli.run(["groups", "add-user", "groupb1", "user1"])
    cli.run(["machines", "add", "machine1", PUBKEY])
    cli.run(["groups", "add-machine", "group1", "machine1"])

    # Should this fail?
    cli.run(["groups", "add-machine", "group1", "machine1"])

    cli.run(["users", "add", "user1", PUBKEY])
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
    clan_flake: Path, capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    cli = SecretCli()
    capsys.readouterr()  # empty the buffer
    cli.run(["list"])
    assert capsys.readouterr().out == ""

    with pytest.raises(ClanError):  # does not exist yet
        cli.run(["get", "nonexisting"])
    with mock_env(
        SOPS_NIX_SECRET="foo", SOPS_AGE_KEY_FILE=str(clan_flake / ".." / "age.key")
    ):
        cli.run(["set", "key"])
        capsys.readouterr()
        cli.run(["get", "key"])
        assert capsys.readouterr().out == "foo"

        capsys.readouterr()  # empty the buffer
        cli.run(["list"])
        assert capsys.readouterr().out == "key\n"

        cli.run(["machines", "add", "machine1", PUBKEY])
        cli.run(["machines", "add-secret", "machine1", "key"])

        with mock_env(SOPS_AGE_KEY=PRIVKEY, SOPS_AGE_KEY_FILE=""):
            capsys.readouterr()
            cli.run(["get", "key"])
            assert capsys.readouterr().out == "foo"
        cli.run(["machines", "remove-secret", "machine1", "key"])

        cli.run(["users", "add", "user1", PUBKEY_2])
        cli.run(["users", "add-secret", "user1", "key"])
        with mock_env(SOPS_AGE_KEY=PRIVKEY_2, SOPS_AGE_KEY_FILE=""):
            capsys.readouterr()
            cli.run(["get", "key"])
            assert capsys.readouterr().out == "foo"
        cli.run(["users", "remove-secret", "user1", "key"])

        with pytest.raises(ClanError):  # does not exist yet
            cli.run(["groups", "add-secret", "admin-group", "key"])
        cli.run(["groups", "add-user", "admin-group", "user1"])
        cli.run(["groups", "add-secret", "admin-group", "key"])

        with mock_env(SOPS_AGE_KEY=PRIVKEY_2, SOPS_AGE_KEY_FILE=""):
            capsys.readouterr()
            cli.run(["get", "key"])
            assert capsys.readouterr().out == "foo"
        cli.run(["groups", "remove-secret", "admin-group", "key"])

    cli.run(["remove", "key"])

    capsys.readouterr()  # empty the buffer
    cli.run(["list"])
    assert capsys.readouterr().out == ""
