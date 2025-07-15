from pathlib import Path

import pytest
from clan_cli.tests.helpers import cli
from clan_lib.errors import ClanError


def test_get_command_no_flake(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ClanError):
        cli.run(["vars", "get", "machine1", "var1"])
