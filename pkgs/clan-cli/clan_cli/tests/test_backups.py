import pytest
from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_cli.tests.helpers import cli


@pytest.mark.impure
def test_backups(
    test_flake_with_core: FlakeForTest,
) -> None:
    cli.run(
        [
            "backups",
            "list",
            "--flake",
            str(test_flake_with_core.path),
            "vm1",
        ]
    )
