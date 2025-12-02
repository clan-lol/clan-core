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
from clan_lib.machines.machines import Machine


@pytest.mark.with_core
def test_should_prompt_for_hardware_config(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    """Test should_prompt_for_hardware_config with various conditions."""
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)
    machine_dir.mkdir(parents=True, exist_ok=True)

    facter_file = machine_dir / "facter.json"
    hardware_file = machine_dir / "hardware-configuration.nix"

    # Clean slate - no config files
    facter_file.unlink(missing_ok=True)
    hardware_file.unlink(missing_ok=True)

    # With --yes flag -> False (even without config)
    args = argparse.Namespace(yes=True, update_hardware_config="none")
    assert not should_prompt_for_hardware_config(machine, args)

    # With explicit --update-hardware-config -> False
    args = argparse.Namespace(yes=False, update_hardware_config="nixos-facter")
    assert not should_prompt_for_hardware_config(machine, args)

    # Non-interactive (stdin not TTY) -> False
    args = argparse.Namespace(yes=False, update_hardware_config="none")
    with patch("sys.stdin.isatty", return_value=False):
        assert not should_prompt_for_hardware_config(machine, args)

    # With existing facter.json -> False (no need to prompt)
    facter_file.write_text('{"system": "x86_64-linux"}')
    args = argparse.Namespace(yes=False, update_hardware_config="none")
    assert not should_prompt_for_hardware_config(machine, args)
    facter_file.unlink()

    # With existing hardware-configuration.nix -> False (no need to prompt)
    hardware_file.write_text("{ ... }: { }")
    args = argparse.Namespace(yes=False, update_hardware_config="none")
    assert not should_prompt_for_hardware_config(machine, args)
    hardware_file.unlink()


@pytest.mark.with_core
def test_should_prompt_for_facter_update(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    """Test should_prompt_for_facter_update with various conditions."""
    machine = Machine(name="vm1", flake=Flake(str(test_flake_with_core.path)))
    machine_dir = specific_machine_dir(machine)
    machine_dir.mkdir(parents=True, exist_ok=True)

    facter_file = machine_dir / "facter.json"

    # Clean slate
    facter_file.unlink(missing_ok=True)

    # No facter.json -> False (nothing to update)
    args = argparse.Namespace(yes=False, update_hardware_config="none")
    assert not should_prompt_for_facter_update(machine, args)

    # Create facter.json for remaining tests
    facter_file.write_text('{"system": "x86_64-linux"}')

    # Interactive mode with facter.json -> True (should prompt for update)
    args = argparse.Namespace(yes=False, update_hardware_config="none")
    with patch("sys.stdin.isatty", return_value=True):
        assert should_prompt_for_facter_update(machine, args)

    # With --yes flag -> False
    args = argparse.Namespace(yes=True, update_hardware_config="none")
    assert not should_prompt_for_facter_update(machine, args)

    # With explicit --update-hardware-config -> False
    args = argparse.Namespace(yes=False, update_hardware_config="nixos-facter")
    assert not should_prompt_for_facter_update(machine, args)

    # Cleanup
    facter_file.unlink()
