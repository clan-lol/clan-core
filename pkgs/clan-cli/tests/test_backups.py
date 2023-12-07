import pytest
from cli import Cli
from fixtures_flakes import FlakeForTest


@pytest.mark.impure
def test_backups(
    test_flake_with_core: FlakeForTest,
) -> None:
    cli = Cli()

    cli.run(
        [
            "--flake",
            str(test_flake_with_core.path),
            "backups",
            "list",
            "vm1",
        ]
    )
