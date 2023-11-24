import os
from typing import TYPE_CHECKING

import pytest
from cli import Cli
from fixtures_flakes import FlakeForTest

if TYPE_CHECKING:
    from age_keys import KeyPair

no_kvm = not os.path.exists("/dev/kvm")


@pytest.mark.impure
def test_inspect(
    test_flake_with_core: FlakeForTest, capsys: pytest.CaptureFixture
) -> None:
    cli = Cli()
    cli.run(["--flake", str(test_flake_with_core.path), "vms", "inspect", "vm1"])
    out = capsys.readouterr()  # empty the buffer
    assert "Cores" in out.out


@pytest.mark.skipif(no_kvm, reason="Requires KVM")
@pytest.mark.impure
def test_run(
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
            "user1",
            age_keys[0].pubkey,
        ]
    )
    cli.run(["vms", "run", "vm1"])
