from typing import TYPE_CHECKING

import pytest
from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_cli.tests.helpers import cli
from clan_cli.tests.stdout import CaptureOutput

if TYPE_CHECKING:
    pass


@pytest.mark.impure
def test_flakes_inspect(
    test_flake_with_core: FlakeForTest, capture_output: CaptureOutput
) -> None:
    with capture_output as output:
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
    assert "Icon" in output.out
