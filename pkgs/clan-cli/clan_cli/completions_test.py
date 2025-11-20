"""Tests for dynamic completion functionality.

These tests verify that dynamic completions work correctly for various commands.
The tests directly call completion functions rather than simulating shell completion.
"""

import argparse
import inspect

import pytest
from clan_lib.flake import Flake

from . import completions
from .completions import complete_machines
from .tests import fixtures_flakes
from .tests.helpers import cli


@pytest.fixture(autouse=True)
def increase_completion_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Increase completion timeout for tests to avoid flakiness in CI."""
    monkeypatch.setattr(completions, "COMPLETION_TIMEOUT", 10)


@pytest.mark.with_core
def test_complete_machines(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    """Test that complete_machines returns the correct machine names."""
    parsed_args = argparse.Namespace(flake=Flake(str(test_flake_with_core.path)))

    completions = complete_machines(prefix="", parsed_args=parsed_args)

    completion_list = (
        list(completions.keys()) if isinstance(completions, dict) else list(completions)
    )

    assert "vm1" in completion_list, (
        f"Expected 'vm1' in completions, got: {completion_list}"
    )
    assert "vm2" in completion_list, (
        f"Expected 'vm2' in completions, got: {completion_list}"
    )


@pytest.mark.with_core
def test_complete_machines_with_prefix(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    parsed_args = argparse.Namespace(flake=Flake(str(test_flake_with_core.path)))

    completions = complete_machines(prefix="vm", parsed_args=parsed_args)
    completion_list = (
        list(completions.keys()) if isinstance(completions, dict) else list(completions)
    )

    assert len(completion_list) > 0, "Should return machine names"


@pytest.mark.with_core
def test_complete_machines_without_flake(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that complete_machines works when flake is not explicitly set.

    When no --flake argument is provided, completions should use the current
    directory or CLAN_DIR environment variable.
    """
    monkeypatch.chdir(test_flake_with_core.path)

    parsed_args = argparse.Namespace()

    completions = complete_machines(prefix="", parsed_args=parsed_args)
    completion_list = (
        list(completions.keys()) if isinstance(completions, dict) else list(completions)
    )

    assert "vm1" in completion_list
    assert "vm2" in completion_list


@pytest.mark.with_core
def test_complete_machines_with_created_machine(
    test_flake_with_core: fixtures_flakes.FlakeForTest,
) -> None:
    """Test that completions include dynamically created machines."""
    # Create a new machine
    cli.run(
        [
            "machines",
            "create",
            "--flake",
            str(test_flake_with_core.path),
            "test-machine",
        ],
    )

    parsed_args = argparse.Namespace(flake=Flake(str(test_flake_with_core.path)))
    completions = complete_machines(prefix="", parsed_args=parsed_args)
    completion_list = (
        list(completions.keys()) if isinstance(completions, dict) else list(completions)
    )

    # Should include the newly created machine
    assert "test-machine" in completion_list, (
        f"Expected 'test-machine' in {completion_list}"
    )
    assert "vm1" in completion_list
    assert "vm2" in completion_list


def test_complete_machines_signature() -> None:
    """Test that complete_machines has the correct signature for argcomplete."""
    sig = inspect.signature(complete_machines)
    params = list(sig.parameters.keys())

    assert params[0] == "prefix", (
        f"First parameter should be 'prefix' for argcomplete compatibility, got: {params[0]}"
    )
