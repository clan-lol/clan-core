import json
import logging
import os
import random
import re
import string
from collections.abc import Iterator
from contextlib import contextmanager
from typing import TYPE_CHECKING

import pytest
from clan_cli.tests.age_keys import assert_secrets_file_recipients
from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_cli.tests.gpg_keys import GpgKey
from clan_cli.tests.helpers import cli
from clan_cli.tests.stdout import CaptureOutput
from clan_lib.errors import ClanError

if TYPE_CHECKING:
    from .age_keys import KeyPair

log = logging.getLogger(__name__)


@pytest.mark.with_core
def _test_identities(
    what: str,
    test_flake_with_core: FlakeForTest,
    capture_output: CaptureOutput,
    age_keys: list["KeyPair"],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sops_folder = test_flake_with_core.path / "sops"

    what_singular = what[:-1]
    test_secret_name = f"{what_singular}_secret"

    # fake some admin user that's different from the identity, we are going to
    # try to add/remove/update from the clan, this way we can check that keys
    # are properly updated on secrets when an identity changes.
    admin_age_key = age_keys[2]

    cli.run(
        [
            "secrets",
            what,
            "add",
            "--flake",
            str(test_flake_with_core.path),
            "foo",
            age_keys[0].pubkey,
        ]
    )
    assert (sops_folder / what / "foo" / "key.json").exists()

    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(test_flake_with_core.path),
            "admin",
            admin_age_key.pubkey,
        ]
    )

    with pytest.raises(ClanError):  # raises "foo already exists"
        cli.run(
            [
                "secrets",
                what,
                "add",
                "--flake",
                str(test_flake_with_core.path),
                "foo",
                age_keys[0].pubkey,
            ]
        )

    with monkeypatch.context() as m:
        m.setenv("SOPS_NIX_SECRET", "deadfeed")
        m.setenv("SOPS_AGE_KEY", admin_age_key.privkey)

        cli.run(
            [
                "secrets",
                "set",
                "--flake",
                str(test_flake_with_core.path),
                f"--{what_singular}",
                "foo",
                test_secret_name,
            ]
        )

    assert_secrets_file_recipients(
        test_flake_with_core.path,
        test_secret_name,
        expected_age_recipients_keypairs=[age_keys[0], admin_age_key],
    )

    with monkeypatch.context():
        monkeypatch.setenv("SOPS_AGE_KEY", admin_age_key.privkey)
        cli.run(
            [
                "secrets",
                what,
                "add",
                "--flake",
                str(test_flake_with_core.path),
                "-f",
                "foo",
                age_keys[1].privkey,
            ]
        )
    assert_secrets_file_recipients(
        test_flake_with_core.path,
        test_secret_name,
        expected_age_recipients_keypairs=[age_keys[1], admin_age_key],
    )

    with capture_output as output:
        cli.run(
            [
                "secrets",
                what,
                "get",
                "--flake",
                str(test_flake_with_core.path),
                "foo",
            ]
        )
    assert age_keys[1].pubkey in output.out

    with capture_output as output:
        cli.run(["secrets", what, "list", "--flake", str(test_flake_with_core.path)])
    assert "foo" in output.out

    cli.run(
        ["secrets", what, "remove", "--flake", str(test_flake_with_core.path), "foo"]
    )
    assert not (sops_folder / what / "foo" / "key.json").exists()

    with pytest.raises(ClanError):  # already removed
        cli.run(
            [
                "secrets",
                what,
                "remove",
                "--flake",
                str(test_flake_with_core.path),
                "foo",
            ]
        )

    with capture_output as output:
        cli.run(["secrets", what, "list", "--flake", str(test_flake_with_core.path)])
    assert "foo" not in output.out

    user_or_machine_symlink = sops_folder / "secrets" / test_secret_name / what / "foo"
    err_msg = (
        f"Symlink to {what_singular} foo's key in secret "
        f"{test_secret_name} was not cleaned up after "
        f"{what_singular} foo was removed."
    )
    assert not user_or_machine_symlink.exists(follow_symlinks=False), err_msg


@pytest.mark.with_core
def test_users(
    test_flake_with_core: FlakeForTest,
    capture_output: CaptureOutput,
    age_keys: list["KeyPair"],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with monkeypatch.context():
        _test_identities(
            "users", test_flake_with_core, capture_output, age_keys, monkeypatch
        )


@pytest.mark.with_core
def test_multiple_user_keys(
    test_flake_with_core: FlakeForTest,
    capture_output: CaptureOutput,
    age_keys: list["KeyPair"],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sops_folder = test_flake_with_core.path / "sops"

    users_keys = {
        "bob": {age_keys[0], age_keys[1]},
        "alice": {age_keys[2]},
        "charlie": {age_keys[3], age_keys[4], age_keys[5]},
    }

    for user, user_keys in users_keys.items():
        # add the user
        cli.run(
            [
                "secrets",
                "users",
                "add",
                "--flake",
                str(test_flake_with_core.path),
                user,
                *[f"--age-key={key.pubkey}" for key in user_keys],
            ]
        )
        assert (sops_folder / "users" / user / "key.json").exists()

        # check they are returned in get
        with capture_output as output:
            cli.run(
                [
                    "secrets",
                    "users",
                    "get",
                    "--flake",
                    str(test_flake_with_core.path),
                    user,
                ]
            )

        for user_key in user_keys:
            assert user_key.pubkey in output.out

        # let's do some setting and getting of secrets

        def random_str() -> str:
            return "".join(random.choices(string.ascii_letters, k=10))

        for user_key in user_keys:
            # set a secret using each of the user's private keys
            with monkeypatch.context():
                secret_name = f"{user}_secret_{random_str()}"
                secret_value = random_str()

                monkeypatch.setenv("SOPS_AGE_KEY", user_key.privkey)
                monkeypatch.setenv("SOPS_NIX_SECRET", secret_value)

                cli.run(
                    [
                        "secrets",
                        "set",
                        "--flake",
                        str(test_flake_with_core.path),
                        secret_name,
                    ]
                )

                # check the secret has each of our user's keys as a recipient
                assert_secrets_file_recipients(
                    test_flake_with_core.path,
                    secret_name,
                    expected_age_recipients_keypairs=[*user_keys],
                )

                # check we can get the secret
                with capture_output as output:
                    cli.run(
                        [
                            "secrets",
                            "get",
                            "--flake",
                            str(test_flake_with_core.path),
                            secret_name,
                        ]
                    )

                assert secret_value in output.out

        if len(user_keys) == 1:
            continue

        # remove one of the user keys,
        user_keys_iter = iter(user_keys)

        key_to_remove = next(user_keys_iter)
        key_to_encrypt_with = next(user_keys_iter)

        with monkeypatch.context():
            monkeypatch.setenv("SOPS_AGE_KEY", key_to_encrypt_with.privkey)
            monkeypatch.setenv("SOPS_NIX_SECRET", "deafbeef")

            cli.run(
                [
                    "secrets",
                    "users",
                    "remove-key",
                    "--flake",
                    str(test_flake_with_core.path),
                    user,
                    key_to_remove.pubkey,
                ]
            )

            # check the secret has been updated
            assert_secrets_file_recipients(
                test_flake_with_core.path,
                secret_name,
                expected_age_recipients_keypairs=list({*user_keys} - {key_to_remove}),
            )

            # add the key back
            cli.run(
                [
                    "secrets",
                    "users",
                    "add-key",
                    "--flake",
                    str(test_flake_with_core.path),
                    user,
                    key_to_remove.pubkey,
                ]
            )

            # check the secret has been updated
            assert_secrets_file_recipients(
                test_flake_with_core.path,
                secret_name,
                expected_age_recipients_keypairs=user_keys,
            )


@pytest.mark.with_core
def test_machines(
    test_flake_with_core: FlakeForTest,
    capture_output: CaptureOutput,
    age_keys: list["KeyPair"],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _test_identities(
        "machines", test_flake_with_core, capture_output, age_keys, monkeypatch
    )


@pytest.mark.with_core
def test_groups(
    test_flake_with_core: FlakeForTest,
    capture_output: CaptureOutput,
    age_keys: list["KeyPair"],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with capture_output as output:
        cli.run(
            ["secrets", "groups", "list", "--flake", str(test_flake_with_core.path)]
        )
    assert output.out == ""

    machine1_age_key = age_keys[0]
    user1_age_key = age_keys[1]
    admin_age_key = age_keys[2]

    with pytest.raises(ClanError):  # machine does not exist yet
        cli.run(
            [
                "secrets",
                "groups",
                "add-machine",
                "--flake",
                str(test_flake_with_core.path),
                "group1",
                "machine1",
            ]
        )
    with pytest.raises(ClanError):  # user does not exist yet
        cli.run(
            [
                "secrets",
                "groups",
                "add-user",
                "--flake",
                str(test_flake_with_core.path),
                "groupb1",
                "user1",
            ]
        )
    cli.run(
        [
            "secrets",
            "machines",
            "add",
            "--flake",
            str(test_flake_with_core.path),
            "machine1",
            machine1_age_key.pubkey,
        ]
    )
    cli.run(
        [
            "secrets",
            "groups",
            "add-machine",
            "--flake",
            str(test_flake_with_core.path),
            "group1",
            "machine1",
        ]
    )

    # Should this fail?
    cli.run(
        [
            "secrets",
            "groups",
            "add-machine",
            "--flake",
            str(test_flake_with_core.path),
            "group1",
            "machine1",
        ]
    )

    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(test_flake_with_core.path),
            "user1",
            user1_age_key.pubkey,
        ]
    )
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(test_flake_with_core.path),
            "admin",
            admin_age_key.pubkey,
        ]
    )
    cli.run(
        [
            "secrets",
            "groups",
            "add-user",
            "--flake",
            str(test_flake_with_core.path),
            "group1",
            "user1",
        ]
    )

    with capture_output as output:
        cli.run(
            ["secrets", "groups", "list", "--flake", str(test_flake_with_core.path)]
        )
    out = output.out
    assert "user1" in out
    assert "machine1" in out

    secret_name = "foo"

    with monkeypatch.context():
        monkeypatch.setenv("SOPS_NIX_SECRET", "deafbeef")
        monkeypatch.setenv("SOPS_AGE_KEY", admin_age_key.privkey)

        cli.run(
            [
                "secrets",
                "set",
                "--flake",
                str(test_flake_with_core.path),
                "--group",
                "group1",
                secret_name,
            ]
        )

    assert_secrets_file_recipients(
        test_flake_with_core.path,
        secret_name,
        expected_age_recipients_keypairs=[
            machine1_age_key,
            user1_age_key,
            admin_age_key,
        ],
        err_msg=(
            f"The secret `{secret_name}` owned by group1 was not encrypted "
            f"with all members of the group."
        ),
    )

    cli.run(
        [
            "secrets",
            "groups",
            "remove-user",
            "--flake",
            str(test_flake_with_core.path),
            "group1",
            "user1",
        ]
    )
    assert_secrets_file_recipients(
        test_flake_with_core.path,
        secret_name,
        expected_age_recipients_keypairs=[machine1_age_key, admin_age_key],
        err_msg=(
            f"The secret `{secret_name}` owned by group1 is still encrypted for "
            f"`user1` even though this user has been removed from the group."
        ),
    )

    # re-add the user to the group
    cli.run(
        [
            "secrets",
            "groups",
            "add-user",
            "--flake",
            str(test_flake_with_core.path),
            "group1",
            "user1",
        ]
    )
    assert_secrets_file_recipients(
        test_flake_with_core.path,
        secret_name,
        expected_age_recipients_keypairs=[
            machine1_age_key,
            user1_age_key,
            admin_age_key,
        ],
    )
    # and instead of removing the user from the group, remove the
    # user instead, it should also remove it from the group:
    cli.run(
        [
            "secrets",
            "users",
            "remove",
            "--flake",
            str(test_flake_with_core.path),
            "user1",
        ]
    )
    assert_secrets_file_recipients(
        test_flake_with_core.path,
        secret_name,
        expected_age_recipients_keypairs=[machine1_age_key, admin_age_key],
        err_msg=(
            f"The secret `{secret_name}` owned by group1 is still encrypted "
            f"for `user1` even though this user has been deleted."
        ),
    )

    cli.run(
        [
            "secrets",
            "groups",
            "remove-machine",
            "--flake",
            str(test_flake_with_core.path),
            "group1",
            "machine1",
        ]
    )
    assert_secrets_file_recipients(
        test_flake_with_core.path,
        secret_name,
        expected_age_recipients_keypairs=[admin_age_key],
        err_msg=(
            f"The secret `{secret_name}` owned by group1 is still encrypted for "
            f"`machine1` even though this machine has been removed from the group."
        ),
    )

    first_group = next((test_flake_with_core.path / "sops" / "groups").iterdir(), None)
    assert first_group is None

    # Check if the symlink to the group was removed from our foo test secret:
    group_symlink = test_flake_with_core.path / "sops/secrets/foo/groups/group1"
    err_msg = (
        "Symlink to group1's key in foo secret "
        "was not cleaned up after group1 was removed"
    )
    assert not group_symlink.exists(follow_symlinks=False), err_msg


@contextmanager
def use_age_key(key: str, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    old_key = os.environ["SOPS_AGE_KEY_FILE"]
    monkeypatch.delenv("SOPS_AGE_KEY_FILE")
    monkeypatch.setenv("SOPS_AGE_KEY", key)
    try:
        yield
    finally:
        monkeypatch.delenv("SOPS_AGE_KEY")
        monkeypatch.setenv("SOPS_AGE_KEY_FILE", old_key)


@contextmanager
def use_gpg_key(key: GpgKey, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    old_key_file = os.environ.get("SOPS_AGE_KEY_FILE")
    old_key = os.environ.get("SOPS_AGE_KEY")
    monkeypatch.delenv("SOPS_AGE_KEY_FILE", raising=False)
    monkeypatch.delenv("SOPS_AGE_KEY", raising=False)
    monkeypatch.setenv("SOPS_PGP_FP", key.fingerprint)
    try:
        yield
    finally:
        monkeypatch.delenv("SOPS_PGP_FP")
        if old_key_file is not None:
            monkeypatch.setenv("SOPS_AGE_KEY_FILE", old_key_file)
        if old_key is not None:
            monkeypatch.setenv("SOPS_AGE_KEY", old_key)


@pytest.mark.with_core
def test_secrets(
    test_flake_with_core: FlakeForTest,
    capture_output: CaptureOutput,
    monkeypatch: pytest.MonkeyPatch,
    gpg_key: GpgKey,
    age_keys: list["KeyPair"],
) -> None:
    with capture_output as output:
        cli.run(["secrets", "list", "--flake", str(test_flake_with_core.path)])
    assert output.out == ""

    # Generate a new key for the clan
    monkeypatch.setenv(
        "SOPS_AGE_KEY_FILE", str(test_flake_with_core.path / ".." / "age.key")
    )
    with capture_output as output:
        cli.run(
            ["secrets", "key", "generate", "--flake", str(test_flake_with_core.path)]
        )
    assert "age private key" in output.out
    # Read the key that was generated
    with capture_output as output:
        cli.run(["secrets", "key", "show", "--flake", str(test_flake_with_core.path)])

    key = json.loads(output.out)[0]
    assert key["publickey"].startswith("age1")
    # Add testuser with the key that was generated for the clan
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(test_flake_with_core.path),
            "testuser",
            key["publickey"],
        ]
    )

    with pytest.raises(ClanError):  # does not exist yet
        cli.run(
            ["secrets", "get", "--flake", str(test_flake_with_core.path), "nonexisting"]
        )
    monkeypatch.setenv("SOPS_NIX_SECRET", "foo")
    cli.run(["secrets", "set", "--flake", str(test_flake_with_core.path), "initialkey"])
    with capture_output as output:
        cli.run(
            ["secrets", "get", "--flake", str(test_flake_with_core.path), "initialkey"]
        )
    assert output.out == "foo"
    with capture_output as output:
        cli.run(["secrets", "users", "list", "--flake", str(test_flake_with_core.path)])
    users = output.out.rstrip().split("\n")
    assert len(users) == 1, f"users: {users}"
    owner = users[0]

    monkeypatch.setenv("EDITOR", "cat")
    cli.run(
        [
            "secrets",
            "set",
            "--edit",
            "--flake",
            str(test_flake_with_core.path),
            "initialkey",
        ]
    )
    monkeypatch.delenv("EDITOR")

    cli.run(
        [
            "secrets",
            "rename",
            "--flake",
            str(test_flake_with_core.path),
            "initialkey",
            "key",
        ]
    )

    with capture_output as output:
        cli.run(["secrets", "list", "--flake", str(test_flake_with_core.path)])
    assert output.out == "key\n"

    with capture_output as output:
        cli.run(
            [
                "secrets",
                "list",
                "--flake",
                str(test_flake_with_core.path),
                "nonexisting",
            ]
        )
    assert output.out == ""

    with capture_output as output:
        cli.run(["secrets", "list", "--flake", str(test_flake_with_core.path), "key"])
    assert output.out == "key\n"

    # using the `age_keys` KeyPair, add a machine and rotate its key

    cli.run(
        [
            "secrets",
            "machines",
            "add",
            "--flake",
            str(test_flake_with_core.path),
            "machine1",
            age_keys[1].pubkey,
        ]
    )
    cli.run(
        [
            "secrets",
            "machines",
            "add-secret",
            "--flake",
            str(test_flake_with_core.path),
            "machine1",
            "key",
        ]
    )
    with capture_output as output:
        cli.run(
            ["secrets", "machines", "list", "--flake", str(test_flake_with_core.path)]
        )
    assert output.out == "machine1\n"

    with use_age_key(age_keys[1].privkey, monkeypatch):
        with capture_output as output:
            cli.run(
                ["secrets", "get", "--flake", str(test_flake_with_core.path), "key"]
            )
        assert output.out == "foo"

    # rotate machines key
    cli.run(
        [
            "secrets",
            "machines",
            "add",
            "--flake",
            str(test_flake_with_core.path),
            "-f",
            "machine1",
            age_keys[0].privkey,
        ]
    )

    # should also rotate the encrypted secret
    with use_age_key(age_keys[0].privkey, monkeypatch):
        with capture_output as output:
            cli.run(
                ["secrets", "get", "--flake", str(test_flake_with_core.path), "key"]
            )
        assert output.out == "foo"

    cli.run(
        [
            "secrets",
            "machines",
            "remove-secret",
            "--flake",
            str(test_flake_with_core.path),
            "machine1",
            "key",
        ]
    )

    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(test_flake_with_core.path),
            "user1",
            age_keys[1].pubkey,
        ]
    )
    cli.run(
        [
            "secrets",
            "users",
            "add-secret",
            "--flake",
            str(test_flake_with_core.path),
            "user1",
            "key",
        ]
    )
    with capture_output as output, use_age_key(age_keys[1].privkey, monkeypatch):
        cli.run(["secrets", "get", "--flake", str(test_flake_with_core.path), "key"])
    assert output.out == "foo"
    cli.run(
        [
            "secrets",
            "users",
            "remove-secret",
            "--flake",
            str(test_flake_with_core.path),
            "user1",
            "key",
        ]
    )

    with pytest.raises(ClanError):  # does not exist yet
        cli.run(
            [
                "secrets",
                "groups",
                "add-secret",
                "--flake",
                str(test_flake_with_core.path),
                "admin-group",
                "key",
            ]
        )
    cli.run(
        [
            "secrets",
            "groups",
            "add-user",
            "--flake",
            str(test_flake_with_core.path),
            "admin-group",
            "user1",
        ]
    )
    cli.run(
        [
            "secrets",
            "groups",
            "add-user",
            "--flake",
            str(test_flake_with_core.path),
            "admin-group",
            owner,
        ]
    )
    cli.run(
        [
            "secrets",
            "groups",
            "add-secret",
            "--flake",
            str(test_flake_with_core.path),
            "admin-group",
            "key",
        ]
    )

    cli.run(
        [
            "secrets",
            "set",
            "--flake",
            str(test_flake_with_core.path),
            "--group",
            "admin-group",
            "key2",
        ]
    )

    with use_age_key(age_keys[1].privkey, monkeypatch):
        with capture_output as output:
            cli.run(
                ["secrets", "get", "--flake", str(test_flake_with_core.path), "key"]
            )
        assert output.out == "foo"

    # Add an user with a GPG key
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(test_flake_with_core.path),
            "--pgp-key",
            gpg_key.fingerprint,
            "user2",
        ]
    )

    # Extend group will update secrets
    cli.run(
        [
            "secrets",
            "groups",
            "add-user",
            "--flake",
            str(test_flake_with_core.path),
            "admin-group",
            "user2",
        ]
    )

    with use_gpg_key(gpg_key, monkeypatch):  # user2
        with capture_output as output:
            cli.run(
                ["secrets", "get", "--flake", str(test_flake_with_core.path), "key"]
            )
        assert output.out == "foo"

    cli.run(
        [
            "secrets",
            "groups",
            "remove-user",
            "--flake",
            str(test_flake_with_core.path),
            "admin-group",
            "user2",
        ]
    )
    with (
        pytest.raises(ClanError),
        use_gpg_key(gpg_key, monkeypatch),
        capture_output as output,
    ):
        # user2 is not in the group anymore
        cli.run(["secrets", "get", "--flake", str(test_flake_with_core.path), "key"])
    print(output.out)

    cli.run(
        [
            "secrets",
            "groups",
            "remove-secret",
            "--flake",
            str(test_flake_with_core.path),
            "admin-group",
            "key",
        ]
    )

    cli.run(["secrets", "remove", "--flake", str(test_flake_with_core.path), "key"])
    cli.run(["secrets", "remove", "--flake", str(test_flake_with_core.path), "key2"])

    with capture_output as output:
        cli.run(["secrets", "list", "--flake", str(test_flake_with_core.path)])
    assert output.out == ""


@pytest.mark.with_core
def test_secrets_key_generate_gpg(
    test_flake_with_core: FlakeForTest,
    capture_output: CaptureOutput,
    monkeypatch: pytest.MonkeyPatch,
    gpg_key: GpgKey,
) -> None:
    with use_gpg_key(gpg_key, monkeypatch):
        # Make sure clan secrets key generate recognizes
        # the PGP key and does nothing:
        with capture_output as output:
            cli.run(
                [
                    "secrets",
                    "key",
                    "generate",
                    "--flake",
                    str(test_flake_with_core.path),
                ]
            )
        assert "age private key" not in output.out

        assert re.match(r"PGP key.+is already set", output.err), (
            f"expected /PGP key.+is already set/ =~ {output.err}"
        )

        with capture_output as output:
            cli.run(
                ["secrets", "key", "show", "--flake", str(test_flake_with_core.path)]
            )
        key = json.loads(output.out)[0]
        assert key["type"] == "pgp"
        assert key["publickey"] == gpg_key.fingerprint

        # Add testuser with the key that was (not) generated for the clan:
        cli.run(
            [
                "secrets",
                "users",
                "add",
                "--flake",
                str(test_flake_with_core.path),
                "--pgp-key",
                gpg_key.fingerprint,
                "testuser",
            ]
        )

        with capture_output as output:
            cli.run(
                [
                    "secrets",
                    "users",
                    "get",
                    "--flake",
                    str(test_flake_with_core.path),
                    "testuser",
                ]
            )
        keys = json.loads(output.out)
        assert len(keys) == 1

        key = keys[0]
        assert key["type"] == "pgp"
        assert key["publickey"] == gpg_key.fingerprint

        with monkeypatch.context() as m:
            m.setenv("SOPS_NIX_SECRET", "secret-value")

            cli.run(
                [
                    "secrets",
                    "set",
                    "--flake",
                    str(test_flake_with_core.path),
                    "secret-name",
                ]
            )
            with capture_output as output:
                cli.run(
                    [
                        "secrets",
                        "get",
                        "--flake",
                        str(test_flake_with_core.path),
                        "secret-name",
                    ]
                )
            assert output.out == "secret-value"


@pytest.mark.with_core
def test_secrets_users_add_age_plugin_error(
    test_flake_with_core: FlakeForTest,
) -> None:
    """Test that AGE-PLUGIN keys raise proper error message"""
    with pytest.raises(ClanError) as exc_info:
        cli.run(
            [
                "secrets",
                "users",
                "add",
                "--flake",
                str(test_flake_with_core.path),
                "testuser",
                "AGE-PLUGIN-YUBIKEY-18P5XCQVZ5FE4WKCW3NJWP",
            ]
        )

    error_msg = str(exc_info.value)
    assert "AGE-PLUGIN keys cannot be used directly" in error_msg
    assert "plugin identifiers, not recipient keys" in error_msg
    assert "corresponding age1 public key instead" in error_msg
    assert "AGE-PLUGIN-YUBIKEY-18P5XCQVZ5FE4WKCW3NJWP" in error_msg
