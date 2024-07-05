import pytest
from fixtures_flakes import FlakeForTest
from helpers.cli import Cli


@pytest.mark.impure
def test_backups(
    test_flake_with_core: FlakeForTest,
) -> None:
    cli = Cli()

    cli.run(
        [
            "backups",
            "list",
            "--flake",
            str(test_flake_with_core.path),
            "vm1",
        ]
    )
