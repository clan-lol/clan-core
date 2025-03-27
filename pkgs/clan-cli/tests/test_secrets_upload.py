from typing import TYPE_CHECKING

import pytest
from clan_cli.ssh.host import Host
from fixtures_flakes import ClanFlake
from helpers import cli

if TYPE_CHECKING:
    from age_keys import KeyPair


@pytest.mark.with_core
def test_secrets_upload(
    monkeypatch: pytest.MonkeyPatch,
    flake: ClanFlake,
    hosts: list[Host],
    age_keys: list["KeyPair"],
) -> None:
    config = flake.machines["vm1"]
    config["nixpkgs"]["hostPlatform"] = "x86_64-linux"
    host = hosts[0]
    addr = f"{host.user}@{host.host}:{host.port}?StrictHostKeyChecking=no&UserKnownHostsFile=/dev/null&IdentityFile={host.key}"
    config["clan"]["networking"]["targetHost"] = addr
    config["clan"]["core"]["facts"]["secretUploadDirectory"] = str(flake.path / "facts")
    flake.refresh()
    monkeypatch.chdir(str(flake.path))
    monkeypatch.setenv("SOPS_AGE_KEY", age_keys[0].privkey)

    sops_dir = flake.path / "facts"

    # the flake defines this path as the location where the sops key should be installed
    sops_key = sops_dir / "key.txt"
    sops_key2 = sops_dir / "key2.txt"

    # Create old state, which should be cleaned up
    sops_dir.mkdir()
    sops_key.write_text("OLD STATE")
    sops_key2.write_text("OLD STATE2")

    cli.run(
        [
            "secrets",
            "users",
            "add",
            "--flake",
            str(flake.path),
            "user1",
            age_keys[0].pubkey,
        ]
    )

    cli.run(
        [
            "secrets",
            "machines",
            "add",
            "--flake",
            str(flake.path),
            "vm1",
            age_keys[1].pubkey,
        ]
    )
    monkeypatch.setenv("SOPS_NIX_SECRET", age_keys[0].privkey)
    cli.run(["secrets", "set", "--flake", str(flake.path), "vm1-age.key"])

    flake_path = flake.path.joinpath("flake.nix")

    cli.run(["facts", "upload", "--flake", str(flake_path), "vm1"])

    assert sops_key.exists()
    assert sops_key.read_text() == age_keys[0].privkey
    assert not sops_key2.exists()
