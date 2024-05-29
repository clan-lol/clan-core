import ipaddress
from typing import TYPE_CHECKING

import pytest
from cli import Cli
from fixtures_flakes import FlakeForTest

from clan_cli.machines.facts import machine_get_fact
from clan_cli.secrets.folders import sops_secrets_folder
from clan_cli.secrets.secrets import has_secret

if TYPE_CHECKING:
    from age_keys import KeyPair


@pytest.mark.impure
def test_generate_secret(
    monkeypatch: pytest.MonkeyPatch,
    test_flake_with_core: FlakeForTest,
    age_keys: list["KeyPair"],
) -> None:
    monkeypatch.chdir(test_flake_with_core.path)
    monkeypatch.setenv("SOPS_AGE_KEY", age_keys[0].privkey)
    cli = Cli()
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
    cmd = ["facts", "generate", "--flake", str(test_flake_with_core.path), "vm1"]
    cli.run(cmd)
    has_secret(test_flake_with_core.path, "vm1-age.key")
    has_secret(test_flake_with_core.path, "vm1-zerotier-identity-secret")
    has_secret(test_flake_with_core.path, "vm1-zerotier-subnet")
    network_id = machine_get_fact(
        test_flake_with_core.path, "vm1", "zerotier-network-id"
    )
    assert len(network_id) == 16
    secrets_folder = sops_secrets_folder(test_flake_with_core.path)
    age_key = secrets_folder / "vm1-age.key" / "secret"
    identity_secret = secrets_folder / "vm1-zerotier-identity-secret" / "secret"
    age_key_mtime = age_key.lstat().st_mtime_ns
    secret1_mtime = identity_secret.lstat().st_mtime_ns

    # test idempotency for vm1 and also generate for vm2
    cli.run(["facts", "generate", "--flake", str(test_flake_with_core.path)])
    assert age_key.lstat().st_mtime_ns == age_key_mtime
    assert identity_secret.lstat().st_mtime_ns == secret1_mtime

    assert (
        secrets_folder / "vm1-zerotier-identity-secret" / "machines" / "vm1"
    ).exists()

    assert has_secret(test_flake_with_core.path, "vm2-age.key")
    assert has_secret(test_flake_with_core.path, "vm2-zerotier-identity-secret")
    ip = machine_get_fact(test_flake_with_core.path, "vm1", "zerotier-ip")
    assert ipaddress.IPv6Address(ip).is_private
