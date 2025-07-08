import pytest

from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_cli.tests.helpers import cli
from clan_cli.tests.stdout import CaptureOutput


@pytest.mark.with_core
def test_clan_show(
    test_flake_with_core: FlakeForTest, capture_output: CaptureOutput
) -> None:
    with capture_output as output:
        cli.run(["show", "--flake", str(test_flake_with_core.path)])
    assert "Name:" in output.out
    assert "Name: test_flake_with_core" in output.out
    assert "Description:" in output.out
