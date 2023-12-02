import json
from typing import TYPE_CHECKING

from cli import Cli
from fixtures_flakes import FlakeForTest
from pytest import CaptureFixture

from clan_cli.dirs import user_history_file
from clan_cli.flakes.history import HistoryEntry

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
    history = [HistoryEntry(**entry) for entry in json.loads(open(history_file).read())]
    assert history[0].path == str(test_flake.path)


def test_flakes_list(
    capsys: CaptureFixture,
    test_flake: FlakeForTest,
) -> None:
    cli = Cli()
    cmd = [
        "flakes",
        "list",
    ]

    cli.run(cmd)
    assert str(test_flake.path) not in capsys.readouterr().out

    cli.run(["flakes", "add", str(test_flake.path)])
    cli.run(cmd)
    assert str(test_flake.path) in capsys.readouterr().out
