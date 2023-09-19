from pathlib import Path

import pytest
from cli import Cli


@pytest.mark.impure
def test_template(monkeypatch: pytest.MonkeyPatch, temporary_dir: Path) -> None:
    monkeypatch.chdir(temporary_dir)
    cli = Cli()
    cli.run(["create"])
    assert (temporary_dir / ".clan-flake").exists()
