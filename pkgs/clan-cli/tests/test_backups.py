import logging

from cli import Cli
from fixtures_flakes import FlakeForTest

log = logging.getLogger(__name__)


def test_backups(
    test_flake: FlakeForTest,
) -> None:
    cli = Cli()

    cli.run(
        [
            "--flake",
            str(test_flake.path),
            "backups",
            "list",
            "testhostname",
        ]
    )
