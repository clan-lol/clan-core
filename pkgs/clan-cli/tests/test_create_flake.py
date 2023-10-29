import json
import subprocess
from pathlib import Path

import pytest
from api import TestClient
from cli import Cli

from clan_cli.dirs import clan_flakes_dir
from clan_cli.flakes.create import DEFAULT_URL


@pytest.fixture
def cli() -> Cli:
    return Cli()


@pytest.mark.impure
def test_create_flake_api(
    monkeypatch: pytest.MonkeyPatch, api: TestClient, temporary_home: Path
) -> None:
    monkeypatch.chdir(clan_flakes_dir())
    flake_name = "flake_dir"
    flake_dir = clan_flakes_dir() / flake_name
    response = api.post(
        "/api/flake/create",
        json=dict(
            flake_name=str(flake_dir),
            url=str(DEFAULT_URL),
        ),
    )

    assert response.status_code == 201, f"Failed to create flake {response.text}"
    assert (flake_dir / ".clan-flake").exists()
    assert (flake_dir / "flake.nix").exists()


@pytest.mark.impure
def test_create_flake(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture,
    temporary_home: Path,
    cli: Cli,
) -> None:
    monkeypatch.chdir(clan_flakes_dir())
    flake_name = "flake_dir"
    flake_dir = clan_flakes_dir() / flake_name

    cli.run(["flakes", "create", flake_name])
    assert (flake_dir / ".clan-flake").exists()
    monkeypatch.chdir(flake_dir)
    cli.run(["machines", "create", "machine1", flake_name])
    capsys.readouterr()  # flush cache

    cli.run(["machines", "list", flake_name])
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
    cli.run(
        ["config", "--machine", "machine1", "services.openssh.enable", "", flake_name]
    )
    capsys.readouterr()
    cli.run(
        [
            "config",
            "--machine",
            "machine1",
            "services.openssh.enable",
            "true",
            flake_name,
        ]
    )
