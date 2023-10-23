from pathlib import Path

import pytest

from clan_cli.dirs import _get_clan_flake_toplevel
from clan_cli.errors import ClanError


def test_get_clan_flake_toplevel(
    monkeypatch: pytest.MonkeyPatch, temporary_home: Path
) -> None:
    monkeypatch.chdir(temporary_home)
    with pytest.raises(ClanError):
        print(_get_clan_flake_toplevel())
    (temporary_home / ".git").touch()
    assert _get_clan_flake_toplevel() == temporary_home

    subdir = temporary_home / "subdir"
    subdir.mkdir()
    monkeypatch.chdir(subdir)
    (subdir / ".clan-flake").touch()
    assert _get_clan_flake_toplevel() == subdir
