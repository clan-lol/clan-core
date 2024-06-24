import ipaddress
import subprocess
import tempfile
from typing import TYPE_CHECKING

import pytest
from age_keys import is_valid_age_key
from cli import Cli
from fixtures_flakes import FlakeForTest

from clan_cli.machines.facts import machine_get_fact
from clan_cli.secrets.folders import sops_secrets_folder
from clan_cli.secrets.secrets import decrypt_secret, has_secret

if TYPE_CHECKING:
    from age_keys import KeyPair


def is_valid_ssh_key(secret_key: str, ssh_pub: str) -> bool:
    # create tempfile and write secret_key to it
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(secret_key.encode("utf-8"))
        temp.flush()
        # Run the ssh-keygen command with the -y flag to check the key format
        result = subprocess.run(
            ["ssh-keygen", "-y", "-f", temp.name], capture_output=True, text=True
        )

        if result.returncode == 0:
            if result.stdout != ssh_pub:
                raise ValueError(
                    f"Expected '{ssh_pub}' got '{result.stdout}' for ssh key: {secret_key}"
                )
            return True
        else:
            raise ValueError(f"Invalid ssh key: {secret_key}")


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
    assert has_secret(test_flake_with_core.path, "vm1-age.key")
    assert has_secret(test_flake_with_core.path, "vm1-zerotier-identity-secret")
    network_id = machine_get_fact(
        test_flake_with_core.path, "vm1", "zerotier-network-id"
    )
    assert len(network_id) == 16
    secrets_folder = sops_secrets_folder(test_flake_with_core.path)
    age_key = secrets_folder / "vm1-age.key" / "secret"
    identity_secret = secrets_folder / "vm1-zerotier-identity-secret" / "secret"
    age_key_mtime = age_key.lstat().st_mtime_ns
    secret1_mtime = identity_secret.lstat().st_mtime_ns

    # Assert that the age key is valid
    age_secret = decrypt_secret(test_flake_with_core.path, "vm1-age.key")
    assert age_secret.isprintable()
    assert is_valid_age_key(age_secret)

    # # Assert that the ssh key is valid
    # ssh_secret = decrypt_secret(test_flake_with_core.path, "vm1-ssh.id_ed25519")
    # ssh_pub = machine_get_fact(test_flake_with_core.path, "vm1", "ssh.id_ed25519.pub")
    # assert is_valid_ssh_key(ssh_secret, ssh_pub)

    # test idempotency for vm1 and also generate for vm2
    cli.run(["facts", "generate", "--flake", str(test_flake_with_core.path)])
    assert age_key.lstat().st_mtime_ns == age_key_mtime
    assert identity_secret.lstat().st_mtime_ns == secret1_mtime

    assert (
        secrets_folder / "vm1-zerotier-identity-secret" / "machines" / "vm1"
    ).exists()

    assert has_secret(test_flake_with_core.path, "vm2-password")
    assert has_secret(test_flake_with_core.path, "vm2-password-hash")
    assert has_secret(test_flake_with_core.path, "vm2-user-password")
    assert has_secret(test_flake_with_core.path, "vm2-user-password-hash")
    assert has_secret(test_flake_with_core.path, "vm2-ssh.id_ed25519")
    assert has_secret(test_flake_with_core.path, "vm2-age.key")
    assert has_secret(test_flake_with_core.path, "vm2-zerotier-identity-secret")

    ip = machine_get_fact(test_flake_with_core.path, "vm1", "zerotier-ip")
    assert ipaddress.IPv6Address(ip).is_private

    # Assert that the age key is valid
    age_secret = decrypt_secret(test_flake_with_core.path, "vm2-age.key")
    assert age_secret.isprintable()
    assert is_valid_age_key(age_secret)

    # Assert that the ssh key is valid
    ssh_secret = decrypt_secret(test_flake_with_core.path, "vm2-ssh.id_ed25519")
    ssh_pub = machine_get_fact(test_flake_with_core.path, "vm2", "ssh.id_ed25519.pub")
    assert is_valid_ssh_key(ssh_secret, ssh_pub)

    # Assert that root-password is valid
    pwd_secret = decrypt_secret(test_flake_with_core.path, "vm2-password")
    assert pwd_secret.isprintable()
    assert pwd_secret.isascii()
    pwd_hash = decrypt_secret(test_flake_with_core.path, "vm2-password-hash")
    assert pwd_hash.isprintable()
    assert pwd_hash.isascii()

    # Assert that user-password is valid
    pwd_secret = decrypt_secret(test_flake_with_core.path, "vm2-user-password")
    assert pwd_secret.isprintable()
    assert pwd_secret.isascii()
    pwd_hash = decrypt_secret(test_flake_with_core.path, "vm2-user-password-hash")
    assert pwd_hash.isprintable()
    assert pwd_hash.isascii()
