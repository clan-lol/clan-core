from typing import TYPE_CHECKING

from cli import Cli
from fixtures_flakes import FlakeForTest

from clan_cli.dirs import user_history_file

if TYPE_CHECKING:
    pass


def test_flakes_add(
    test_flake: FlakeForTest,
) -> None:
    cli = Cli()
    cmd = [
        "flakes",
        "add",
        str(test_flake.path),
    ]

    cli.run(cmd)

    history_file = user_history_file()
    assert history_file.exists()
    assert open(history_file).read().strip() == str(test_flake.path)
