import argparse
from unittest.mock import patch

import pytest
from clan_cli.machines.install import (
    should_prompt_for_facter_update,
    should_prompt_for_hardware_config,
)
from clan_cli.tests import fixtures_flakes
from clan_lib.dirs import specific_machine_dir
from clan_lib.flake import Flake
from clan_lib.machines.hardware import has_facter_config, has_hardware_config
from clan_lib.machines.machines import Machine


@pytest.mark.with_core
def test_has_hardware_config_no_config(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)

    # Ensure no hardware config files exist
    (machine_dir / "facter.json").unlink(missing_ok=True)
    (machine_dir / "hardware-configuration.nix").unlink(missing_ok=True)

    assert not has_hardware_config(machine)


@pytest.mark.with_core
def test_has_hardware_config_with_facter(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)
    machine_dir.mkdir(parents=True, exist_ok=True)

    # Create facter.json
    facter_file = machine_dir / "facter.json"
    facter_file.write_text('{"system": "x86_64-linux"}')

    assert has_hardware_config(machine)

    # Clean up
    facter_file.unlink()


@pytest.mark.with_core
def test_has_hardware_config_with_hardware_nix(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)
    machine_dir.mkdir(parents=True, exist_ok=True)

    # Create hardware-configuration.nix
    hardware_file = machine_dir / "hardware-configuration.nix"
    hardware_file.write_text("{ ... }: { }")

    assert has_hardware_config(machine)

    # Clean up
    hardware_file.unlink()


@pytest.mark.with_core
def test_should_prompt_with_yes_flag(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)

    # Ensure no hardware config exists
    (machine_dir / "facter.json").unlink(missing_ok=True)
    (machine_dir / "hardware-configuration.nix").unlink(missing_ok=True)

    args = argparse.Namespace(yes=True, update_hardware_config="none")
    assert not should_prompt_for_hardware_config(machine, args)


@pytest.mark.with_core
def test_should_prompt_with_explicit_hardware_config(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)

    # Ensure no hardware config exists
    (machine_dir / "facter.json").unlink(missing_ok=True)
    (machine_dir / "hardware-configuration.nix").unlink(missing_ok=True)

    args = argparse.Namespace(yes=False, update_hardware_config="nixos-facter")
    assert not should_prompt_for_hardware_config(machine, args)


@pytest.mark.with_core
def test_should_prompt_with_existing_config(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)
    machine_dir.mkdir(parents=True, exist_ok=True)

    # Create facter.json
    facter_file = machine_dir / "facter.json"
    facter_file.write_text('{"system": "x86_64-linux"}')

    args = argparse.Namespace(yes=False, update_hardware_config="none")
    assert not should_prompt_for_hardware_config(machine, args)

    # Clean up
    facter_file.unlink()


@pytest.mark.with_core
def test_should_prompt_non_interactive_no_config(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    """Test should_prompt_for_hardware_config returns False when stdin is not a TTY."""
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)

    # Ensure no hardware config exists
    (machine_dir / "facter.json").unlink(missing_ok=True)
    (machine_dir / "hardware-configuration.nix").unlink(missing_ok=True)

    args = argparse.Namespace(yes=False, update_hardware_config="none")

    # Mock stdin as non-TTY
    with patch("sys.stdin.isatty", return_value=False):
        assert not should_prompt_for_hardware_config(machine, args)


@pytest.mark.with_core
def test_has_facter_config_with_facter(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)
    machine_dir.mkdir(parents=True, exist_ok=True)

    # Create facter.json
    facter_file = machine_dir / "facter.json"
    facter_file.write_text('{"system": "x86_64-linux"}')

    assert has_facter_config(machine)

    # Clean up
    facter_file.unlink()


@pytest.mark.with_core
def test_should_prompt_for_facter_update_interactive_with_facter(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)
    machine_dir.mkdir(parents=True, exist_ok=True)

    # Create facter.json
    facter_file = machine_dir / "facter.json"
    facter_file.write_text('{"system": "x86_64-linux"}')

    args = argparse.Namespace(yes=False, update_hardware_config="none")

    # Mock stdin as TTY for interactive testing
    with patch("sys.stdin.isatty", return_value=True):
        assert should_prompt_for_facter_update(machine, args)

    # Clean up
    facter_file.unlink()


@pytest.mark.with_core
def test_should_prompt_for_facter_update_with_yes_flag(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)
    machine_dir.mkdir(parents=True, exist_ok=True)

    # Create facter.json
    facter_file = machine_dir / "facter.json"
    facter_file.write_text('{"system": "x86_64-linux"}')

    args = argparse.Namespace(yes=True, update_hardware_config="none")
    assert not should_prompt_for_facter_update(machine, args)

    # Clean up
    facter_file.unlink()


@pytest.mark.with_core
def test_should_prompt_for_facter_update_with_explicit_config(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)
    machine_dir.mkdir(parents=True, exist_ok=True)

    # Create facter.json
    facter_file = machine_dir / "facter.json"
    facter_file.write_text('{"system": "x86_64-linux"}')

    args = argparse.Namespace(yes=False, update_hardware_config="nixos-facter")
    assert not should_prompt_for_facter_update(machine, args)

    # Clean up
    facter_file.unlink()


@pytest.mark.with_core
def test_should_prompt_for_facter_update_without_facter(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)

    # Ensure facter.json doesn't exist
    (machine_dir / "facter.json").unlink(missing_ok=True)

    args = argparse.Namespace(yes=False, update_hardware_config="none")
    assert not should_prompt_for_facter_update(machine, args)
