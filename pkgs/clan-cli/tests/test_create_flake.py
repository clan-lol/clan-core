import json
import subprocess
from pathlib import Path

import pytest
from fixtures_flakes import substitute
from helpers import cli
from stdout import CaptureOutput


@pytest.mark.impure
def test_create_flake(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    clan_core: Path,
    capture_output: CaptureOutput,
) -> None:
    flake_dir = temporary_home / "test-flake"

    url = f"{clan_core}#default"
    cli.run(["flakes", "create", str(flake_dir), f"--url={url}"])

    assert (flake_dir / ".clan-flake").exists()
    # Replace the inputs.clan.url in the template flake.nix
    substitute(
        flake_dir / "flake.nix",
        clan_core,
    )
    # Dont evaluate the inventory before the substitute call

    monkeypatch.chdir(flake_dir)
    cli.run(["machines", "create", "machine1"])

    # create a hardware-configuration.nix that doesn't throw an eval error

    for patch_machine in ["jon", "sara"]:
        with open(
            flake_dir / "machines" / f"{patch_machine}/hardware-configuration.nix", "w"
        ) as hw_config_nix:
            hw_config_nix.write("{}")

    with capture_output as output:
        cli.run(["machines", "list"])
    assert "machine1" in output.out
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


@pytest.mark.impure
def test_ui_template(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    clan_core: Path,
    capture_output: CaptureOutput,
) -> None:
    flake_dir = temporary_home / "test-flake"
    url = f"{clan_core}#minimal"
    cli.run(["flakes", "create", str(flake_dir), f"--url={url}"])

    # Replace the inputs.clan.url in the template flake.nix
    substitute(
        flake_dir / "flake.nix",
        clan_core,
    )

    monkeypatch.chdir(flake_dir)
    cli.run(["machines", "create", "machine1"])

    with capture_output as output:
        cli.run(["machines", "list"])
    assert "machine1" in output.out
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
