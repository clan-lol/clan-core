import ipaddress
from typing import TYPE_CHECKING

import pytest
from clan_cli.facts.secret_modules.sops import SecretStore
from clan_cli.flake import Flake
from clan_cli.machines.machines import Machine
from clan_cli.secrets.folders import sops_secrets_folder
from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_cli.tests.helpers import cli
from clan_cli.tests.helpers.validator import is_valid_age_key

if TYPE_CHECKING:
    from .age_keys import KeyPair


@pytest.mark.impure
def test_generate_secret(
    monkeypatch: pytest.MonkeyPatch,
    test_flake_with_core: FlakeForTest,
    age_keys: list["KeyPair"],
) -> None:
    monkeypatch.chdir(test_flake_with_core.path)
    monkeypatch.setenv("SOPS_AGE_KEY", age_keys[0].privkey)
    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(test_flake_with_core.path),
            "user1",
            age_keys[0].pubkey,
        ]
    )
    cli.run(
        [
            "secrets",
            "groups",
            "add-user",
            "--flake",
            str(test_flake_with_core.path),
            "admins",
            "user1",
        ]
    )
    cmd = [
        "vars",
        "generate",
        "--flake",
        str(test_flake_with_core.path),
        "vm1",
        "--generator",
        "zerotier",
    ]
    cli.run(cmd)

    store1 = SecretStore(
        Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    )

    assert store1.exists("", "age.key")
    network_id = (
        test_flake_with_core.path
        / "vars"
        / "per-machine"
        / "vm1"
        / "zerotier"
        / "zerotier-network-id"
        / "value"
    ).read_text()
    assert len(network_id) == 16
    secrets_folder = sops_secrets_folder(test_flake_with_core.path)
    age_key = secrets_folder / "vm1-age.key" / "secret"
    identity_secret = (
        test_flake_with_core.path
        / "vars"
        / "per-machine"
        / "vm1"
        / "zerotier"
        / "zerotier-identity-secret"
        / "secret"
    )
    age_key_mtime = age_key.lstat().st_mtime_ns
    secret1_mtime = identity_secret.lstat().st_mtime_ns

    # Assert that the age key is valid
    age_secret = store1.get("", "age.key").decode()
    assert is_valid_age_key(age_secret)

    # test idempotency for vm1 and also generate for vm2
    cli.run(
        [
            "vars",
            "generate",
            "--flake",
            str(test_flake_with_core.path),
            "--generator",
            "zerotier",
        ]
    )
    assert age_key.lstat().st_mtime_ns == age_key_mtime
    assert identity_secret.lstat().st_mtime_ns == secret1_mtime

    store2 = SecretStore(
        Machine(name="vm2", flake=Flake(str(test_flake_with_core.path)))
    )

    assert store2.exists("", "age.key")
    (
        test_flake_with_core.path
        / "vars"
        / "per-machine"
        / "vm2"
        / "zerotier"
        / "zerotier-identity-secret"
        / "secret"
    ).exists()

    ip = (
        test_flake_with_core.path
        / "vars"
        / "per-machine"
        / "vm2"
        / "zerotier"
        / "zerotier-ip"
        / "value"
    ).read_text()
    assert ipaddress.IPv6Address(ip).is_private

    # Assert that the age key is valid
    age_secret = store2.get("", "age.key").decode()
    assert is_valid_age_key(age_secret)
