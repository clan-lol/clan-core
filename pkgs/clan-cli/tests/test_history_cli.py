import json
from typing import TYPE_CHECKING

import pytest
from fixtures_flakes import FlakeForTest
from helpers import cli
from pytest import CaptureFixture

from clan_cli.dirs import user_history_file
from clan_cli.history.add import HistoryEntry

if TYPE_CHECKING:
    pass


@pytest.mark.impure
def test_history_add(
    test_flake_with_core: FlakeForTest,
) -> None:
    cmd = [
        "history",
        "add",
        f"clan://{test_flake_with_core.path}#vm1",
    ]
    cli.run(cmd)

    history_file = user_history_file()
    assert history_file.exists()
    history = [HistoryEntry(**entry) for entry in json.loads(open(history_file).read())]
    assert history[0].flake.flake_url == str(test_flake_with_core.path)


@pytest.mark.impure
def test_history_list(
    capsys: CaptureFixture,
    test_flake_with_core: FlakeForTest,
) -> None:
    cmd = [
        "history",
        "list",
    ]

    cli.run(cmd)
    assert str(test_flake_with_core.path) not in capsys.readouterr().out

    cli.run(["history", "add", f"clan://{test_flake_with_core.path}#vm1"])
    cli.run(cmd)
    assert str(test_flake_with_core.path) in capsys.readouterr().out
