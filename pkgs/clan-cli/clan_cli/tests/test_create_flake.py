import json
import logging
from pathlib import Path

import pytest
from clan_cli.cmd import run
from clan_cli.tests.fixtures_flakes import FlakeForTest, substitute
from clan_cli.tests.helpers import cli
from clan_cli.tests.stdout import CaptureOutput
from clan_lib.nix import nix_flake_show

log = logging.getLogger(__name__)


@pytest.mark.with_core
def test_create_flake(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    clan_core: Path,
    capture_output: CaptureOutput,
) -> None:
    flake_dir = temporary_home / "test-flake"

    cli.run(["flakes", "create", str(flake_dir), "--template=default", "--no-update"])

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
        (
            flake_dir / "machines" / f"{patch_machine}/hardware-configuration.nix"
        ).write_text("{}")

    with capture_output as output:
        cli.run(["machines", "list"])
    assert "machine1" in output.out
    flake_show = run(
        nix_flake_show(str(flake_dir)),
    )
    flake_outputs = json.loads(flake_show.stdout)
    try:
        flake_outputs["nixosConfigurations"]["machine1"]
    except KeyError:
        pytest.fail("nixosConfigurations.machine1 not found in flake outputs")


@pytest.mark.with_core
def test_create_flake_existing_git(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    clan_core: Path,
    capture_output: CaptureOutput,
) -> None:
    flake_dir = temporary_home / "test-flake"

    run(["git", "init", str(temporary_home)])

    cli.run(["flakes", "create", str(flake_dir), "--template=default", "--no-update"])

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
        (
            flake_dir / "machines" / f"{patch_machine}/hardware-configuration.nix"
        ).write_text("{}")

    with capture_output as output:
        cli.run(["machines", "list"])
    assert "machine1" in output.out
    flake_show = run(
        nix_flake_show(str(flake_dir)),
    )
    flake_outputs = json.loads(flake_show.stdout)
    try:
        flake_outputs["nixosConfigurations"]["machine1"]
    except KeyError:
        pytest.fail("nixosConfigurations.machine1 not found in flake outputs")


@pytest.mark.with_core
def test_ui_template(
    monkeypatch: pytest.MonkeyPatch,
    temporary_home: Path,
    test_flake_with_core: FlakeForTest,
    clan_core: Path,
    capture_output: CaptureOutput,
) -> None:
    flake_dir = temporary_home / "test-flake"

    cli.run(["flakes", "create", str(flake_dir), "--template=minimal", "--no-update"])

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
    flake_show = run(
        nix_flake_show(str(flake_dir)),
    )
    flake_outputs = json.loads(flake_show.stdout)
    try:
        flake_outputs["nixosConfigurations"]["machine1"]
    except KeyError:
        pytest.fail("nixosConfigurations.machine1 not found in flake outputs")
