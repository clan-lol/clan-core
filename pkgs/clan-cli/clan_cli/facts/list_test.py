from pathlib import Path

import pytest
from clan_lib.errors import ClanError

from clan_cli.tests.helpers import cli


def test_list_command_no_flake(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ClanError):
        cli.run(["facts", "list", "machine1"])
