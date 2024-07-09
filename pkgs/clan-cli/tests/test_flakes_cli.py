from typing import TYPE_CHECKING

import pytest
from fixtures_flakes import FlakeForTest
from helpers import cli

if TYPE_CHECKING:
    pass


@pytest.mark.impure
def test_flakes_inspect(
    test_flake_with_core: FlakeForTest, capsys: pytest.CaptureFixture
) -> None:
    cli.run(
        [
            "flakes",
            "inspect",
            "--flake",
            str(test_flake_with_core.path),
            "--machine",
            "vm1",
        ]
    )
    out = capsys.readouterr()  # empty the buffer

    assert "Icon" in out.out
