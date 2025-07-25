from pathlib import Path

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
    assert "Available 'clan' templates" in output.out
    assert "Available 'disko' templates" in output.out
    assert "Available 'machine' templates" in output.out
    assert "single-disk" in output.out
    assert "<builtin>" in output.out
    assert "default:" in output.out
    assert "minimal:" in output.out
    assert "new-machine" in output.out
    assert "flash-installer" in output.out


@pytest.mark.with_core
def test_templates_list_outside_clan(
    capture_output: CaptureOutput, temp_dir: Path
) -> None:
    """Test templates list command when run outside a clan directory."""
    with capture_output as output:
        # Use --flake pointing to a non-clan directory to trigger fallback
        cli.run(["templates", "list", "--flake", str(temp_dir)])
    assert "Available 'clan' templates" in output.out
    assert "Available 'disko' templates" in output.out
    assert "Available 'machine' templates" in output.out
    assert "<builtin>" in output.out
    # Should NOT show any custom templates
    assert "inputs." not in output.out
