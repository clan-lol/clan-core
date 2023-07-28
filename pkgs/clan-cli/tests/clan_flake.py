from pathlib import Path
from typing import Iterator

import pytest
from environment import mock_env


@pytest.fixture
def clan_flake(
    temporary_directory: Path, monkeypatch: pytest.MonkeyPatch
) -> Iterator[Path]:
    flake = temporary_directory / "clan-flake"
    flake.mkdir()
    (flake / ".clan-flake").touch()
    monkeypatch.chdir(flake)
    with mock_env(HOME=str(temporary_directory)):
        yield temporary_directory
