from pathlib import Path

import pytest
from clan_lib.errors import ClanError

from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_cli.tests.helpers import cli
from clan_cli.tests.stdout import CaptureOutput


@pytest.mark.with_core
def test_clan_show(
    test_flake_with_core: FlakeForTest,
    capture_output: CaptureOutput,
) -> None:
    with capture_output as output:
        cli.run(["show", "--flake", str(test_flake_with_core.path)])
    assert "Name:" in output.out
    assert "Name: test_flake_with_core" in output.out
    assert "Description:" in output.out
    assert "Domain:" in output.out


def test_clan_show_no_flake(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ClanError) as exc_info:
        cli.run(["show"])

    assert "No clan flake found in the current directory or its parents" in str(
        exc_info.value,
    )
    assert "Use the --flake flag to specify a clan flake path or URL" in str(
        exc_info.value,
    )
