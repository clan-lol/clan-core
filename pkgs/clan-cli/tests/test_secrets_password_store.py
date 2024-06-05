import subprocess
from pathlib import Path

import pytest
from cli import Cli
from fixtures_flakes import FlakeForTest

from clan_cli.machines.facts import machine_get_fact
from clan_cli.nix import nix_shell
from clan_cli.ssh import HostGroup


@pytest.mark.impure
def test_upload_secret(
    monkeypatch: pytest.MonkeyPatch,
    test_flake_with_core_and_pass: FlakeForTest,
    temporary_home: Path,
    host_group: HostGroup,
) -> None:
    monkeypatch.chdir(test_flake_with_core_and_pass.path)
    gnupghome = temporary_home / "gpg"
    gnupghome.mkdir(mode=0o700)
    monkeypatch.setenv("GNUPGHOME", str(gnupghome))
    monkeypatch.setenv("PASSWORD_STORE_DIR", str(temporary_home / "pass"))
    gpg_key_spec = temporary_home / "gpg_key_spec"
    gpg_key_spec.write_text(
        """
        Key-Type: 1
        Key-Length: 1024
        Name-Real: Root Superuser
        Name-Email: test@local
        Expire-Date: 0
        %no-protection
    """
    )
    cli = Cli()
    subprocess.run(
        nix_shell(
            ["nixpkgs#gnupg"], ["gpg", "--batch", "--gen-key", str(gpg_key_spec)]
        ),
        check=True,
    )
    subprocess.run(
        nix_shell(["nixpkgs#pass"], ["pass", "init", "test@local"]), check=True
    )
    cli.run(["facts", "generate", "vm1"])
    network_id = machine_get_fact(
        test_flake_with_core_and_pass.path, "vm1", "zerotier-network-id"
    )
    assert len(network_id) == 16
    identity_secret = (
        temporary_home / "pass" / "machines" / "vm1" / "zerotier-identity-secret.gpg"
    )
    secret1_mtime = identity_secret.lstat().st_mtime_ns

    # test idempotency
    cli.run(["facts", "generate", "vm1"])
    assert identity_secret.lstat().st_mtime_ns == secret1_mtime
    flake = test_flake_with_core_and_pass.path.joinpath("flake.nix")
    host = host_group.hosts[0]
    addr = f"{host.user}@{host.host}:{host.port}?StrictHostKeyChecking=no&UserKnownHostsFile=/dev/null&IdentityFile={host.key}"
    new_text = flake.read_text().replace("__CLAN_TARGET_ADDRESS__", addr)
    flake.write_text(new_text)
    cli.run(["facts", "upload", "vm1"])
    zerotier_identity_secret = (
        test_flake_with_core_and_pass.path / "secrets" / "zerotier-identity-secret"
    )
    assert zerotier_identity_secret.exists()
