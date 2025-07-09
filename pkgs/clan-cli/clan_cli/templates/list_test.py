import pytest

from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_cli.tests.helpers import cli
from clan_cli.tests.stdout import CaptureOutput


@pytest.mark.with_core
def test_templates_list(
    test_flake_with_core: FlakeForTest, capture_output: CaptureOutput
) -> None:
    with capture_output as output:
        cli.run(["templates", "list", "--flake", str(test_flake_with_core.path)])
    print(output.out)
    assert "Avilable 'clan' templates" in output.out
    assert "Avilable 'disko' templates" in output.out
    assert "Avilable 'machine' templates" in output.out
    assert "single-disk" in output.out
    assert "<builtin>" in output.out
    assert "default:" in output.out
    assert "minimal:" in output.out
    assert "new-machine" in output.out
    assert "flash-installer" in output.out
