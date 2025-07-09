import pytest

from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_cli.tests.helpers import cli
from clan_cli.tests.stdout import CaptureOutput


@pytest.mark.with_core
def test_state_list_vm1(
    test_flake_with_core: FlakeForTest, capture_output: CaptureOutput
) -> None:
    with capture_output as output:
        cli.run(["state", "list", "vm1", "--flake", str(test_flake_with_core.path)])
    assert output.out is not None
    assert "service: zerotier" in output.out
    assert "folders:" in output.out
    assert "/var/lib/zerotier-one" in output.out


@pytest.mark.with_core
def test_state_list_vm2(
    test_flake_with_core: FlakeForTest, capture_output: CaptureOutput
) -> None:
    with capture_output as output:
        cli.run(["state", "list", "vm2", "--flake", str(test_flake_with_core.path)])
    assert output.out is not None
