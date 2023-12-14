import json
import subprocess
from pathlib import Path

import pytest
from cli import Cli


@pytest.fixture
def cli() -> Cli:
    return Cli()


@pytest.mark.impure
def test_create_flake(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    temporary_home: Path,
    cli: Cli,
) -> None:
    flake_dir = temporary_home / "test-flake"

    cli.run(["flakes", "create", str(flake_dir)])
    assert (flake_dir / ".clan-flake").exists()
    monkeypatch.chdir(flake_dir)
    cli.run(["machines", "create", "machine1"])
    capsys.readouterr()  # flush cache

    cli.run(["machines", "list"])
    assert "machine1" in capsys.readouterr().out
    flake_show = subprocess.run(
        ["nix", "flake", "show", "--json"],
        check=True,
        capture_output=True,
        text=True,
    )
    flake_outputs = json.loads(flake_show.stdout)
    try:
        flake_outputs["nixosConfigurations"]["machine1"]
    except KeyError:
        pytest.fail("nixosConfigurations.machine1 not found in flake outputs")
    # configure machine1
    capsys.readouterr()
    cli.run(["config", "--machine", "machine1", "services.openssh.enable", ""])
    capsys.readouterr()
    cli.run(
        [
            "config",
            "--machine",
            "machine1",
            "services.openssh.enable",
            "true",
        ]
    )
