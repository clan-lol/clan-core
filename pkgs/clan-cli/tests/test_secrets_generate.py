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
            "--flake",
            str(test_flake_with_core.path),
            "secrets",
            "users",
            "add",
            "user1",
            age_keys[0].pubkey,
        ]
    )
    cli.run(["--flake", str(test_flake_with_core.path), "secrets", "generate", "vm1"])
    has_secret(test_flake_with_core.path, "vm1-age.key")
    has_secret(test_flake_with_core.path, "vm1-zerotier-identity-secret")
    network_id = machine_get_fact(
        test_flake_with_core.name, "vm1", "zerotier-network-id"
    )
    assert len(network_id) == 16
    age_key = (
        sops_secrets_folder(test_flake_with_core.path)
        .joinpath("vm1-age.key")
        .joinpath("secret")
    )
    identity_secret = (
        sops_secrets_folder(test_flake_with_core.path)
        .joinpath("vm1-zerotier-identity-secret")
        .joinpath("secret")
    )
    age_key_mtime = age_key.lstat().st_mtime_ns
    secret1_mtime = identity_secret.lstat().st_mtime_ns

    # test idempotency
    cli.run(["secrets", "generate", "vm1"])
    assert age_key.lstat().st_mtime_ns == age_key_mtime
    assert identity_secret.lstat().st_mtime_ns == secret1_mtime

    machine_path = (
        sops_secrets_folder(test_flake_with_core.path)
        .joinpath("vm1-zerotier-identity-secret")
        .joinpath("machines")
        .joinpath("vm1")
    )
    assert machine_path.exists()
