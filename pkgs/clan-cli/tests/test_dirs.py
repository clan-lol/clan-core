from pathlib import Path

import pytest

from clan_cli.dirs import get_clan_flake_toplevel
from clan_cli.errors import ClanError


def test_get_clan_flake_toplevel(
    monkeypatch: pytest.MonkeyPatch, temporary_dir: Path
) -> None:
    monkeypatch.chdir(temporary_dir)
    with pytest.raises(ClanError):
        get_clan_flake_toplevel()
