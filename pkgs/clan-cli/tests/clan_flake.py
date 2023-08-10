from pathlib import Path
from typing import Iterator

import pytest
from environment import mock_env


@pytest.fixture
def clan_flake(temporary_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    flake = temporary_dir / "clan-flake"
    flake.mkdir()
    (flake / ".clan-flake").touch()
    (flake / "flake.nix").write_text(
        """
{
    description = "A flake for testing clan";
    inputs = {};
    outputs = { self, nixpkgs }: {};
}
"""
    )
    monkeypatch.chdir(flake)
    with mock_env(HOME=str(temporary_dir)):
        yield flake
