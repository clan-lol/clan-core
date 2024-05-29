from typing import TYPE_CHECKING

import pytest
from cli import Cli
from fixtures_flakes import FlakeForTest

if TYPE_CHECKING:
    pass


@pytest.mark.impure
def test_flakes_inspect(
    test_flake_with_core: FlakeForTest, capsys: pytest.CaptureFixture
) -> None:
    cli = Cli()
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
