import json
import subprocess
from pathlib import Path

import pytest
from api import TestClient
from cli import Cli


@pytest.fixture
def cli() -> Cli:
    return Cli()


@pytest.mark.impure
def test_create_flake_api(
    monkeypatch: pytest.MonkeyPatch, api: TestClient, temporary_dir: Path
) -> None:
    flake_dir = temporary_dir / "flake_dir"
    flake_dir_str = str(flake_dir.resolve())
    response = api.post(
        "/api/flake/create",
        json=dict(
            destination=flake_dir_str,
            url="git+https://git.clan.lol/clan/clan-core#new-clan",
        ),
    )

    assert response.status_code == 201, "Failed to create flake"
    assert (flake_dir / ".clan-flake").exists()
    assert (flake_dir / "flake.nix").exists()


@pytest.mark.impure
def test_create_flake(
    monkeypatch: pytest.MonkeyPatch,
    temporary_dir: Path,
    capsys: pytest.CaptureFixture,
    cli: Cli,
) -> None:
    monkeypatch.chdir(temporary_dir)
    flake_dir = temporary_dir / "flake_dir"
    flake_dir_str = str(flake_dir.resolve())
    cli.run(["flake", "create", flake_dir_str])
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
    cli.run(["config", "--machine", "machine1", "services.openssh.enable"])
    capsys.readouterr()
    cli.run(["config", "--machine", "machine1", "services.openssh.enable", "true"])
