import json
from typing import TYPE_CHECKING

from cli import Cli
from fixtures_flakes import FlakeForTest
from pytest import CaptureFixture

from clan_cli.dirs import user_history_file
from clan_cli.history.add import HistoryEntry

if TYPE_CHECKING:
    pass


def test_history_add(
    test_flake: FlakeForTest,
) -> None:
    cli = Cli()
    cmd = [
        "history",
        "add",
        str(test_flake.path),
    ]
    breakpoint()
    cli.run(cmd)

    history_file = user_history_file()
    assert history_file.exists()
    history = [HistoryEntry(**entry) for entry in json.loads(open(history_file).read())]
    assert history[0].flake.flake_url == str(test_flake.path)


def test_history_list(
    capsys: CaptureFixture,
    test_flake: FlakeForTest,
) -> None:
    cli = Cli()
    cmd = [
        "history",
        "list",
    ]

    cli.run(cmd)
    assert str(test_flake.path) not in capsys.readouterr().out

    cli.run(["history", "add", str(test_flake.path)])
    cli.run(cmd)
    assert str(test_flake.path) in capsys.readouterr().out
