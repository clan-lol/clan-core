import os
from pathlib import Path

import pytest
from cli import Cli

no_kvm = not os.path.exists("/dev/kvm")


@pytest.mark.impure
def test_inspect(test_flake_with_core: Path, capsys: pytest.CaptureFixture) -> None:
    cli = Cli()
    cli.run(["vms", "inspect", "vm1"])
    out = capsys.readouterr()  # empty the buffer
    assert "Cores" in out.out


@pytest.mark.skipif(no_kvm, reason="Requires KVM")
@pytest.mark.impure
def test_create(test_flake_with_core: Path) -> None:
    cli = Cli()
    cli.run(["vms", "create", "vm1"])
