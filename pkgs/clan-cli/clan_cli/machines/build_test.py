from pathlib import Path

import pytest
from clan_lib.errors import ClanError
from clan_lib.flake import Flake

from clan_cli.machines.build import get_machines_for_build
from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_cli.tests.helpers import cli


@pytest.mark.parametrize(
    ("test_flake_with_core", "explicit_names", "filter_tags", "expected_names"),
    [
        (
            {
                "inventory_expr": r"""{
                    machines.jon = { tags = [ "foo" "bar" ]; };
                    machines.sara = { tags = [ "foo" "baz" ]; };
                }""",
            },
            ["jon"],
            [],
            ["jon"],
        ),
        (
            {
                "inventory_expr": r"""{
                    machines.jon = { tags = [ "foo" "bar" ]; };
                    machines.sara = { tags = [ "foo" "baz" ]; };
                }""",
            },
            [],
            [],
            ["jon", "sara", "vm1", "vm2"],
        ),
        (
            {
                "inventory_expr": r"""{
                    machines.jon = { tags = [ "foo" "bar" ]; };
                    machines.sara = { tags = [ "foo" "baz" ]; };
                }""",
            },
            [],
            ["foo"],
            ["jon", "sara"],
        ),
    ],
    indirect=["test_flake_with_core"],
)
@pytest.mark.with_core
def test_get_machines_for_build(
    test_flake_with_core: FlakeForTest,
    explicit_names: list[str],
    filter_tags: list[str],
    expected_names: list[str],
) -> None:
    """Test building machines with various filters (by name, all machines, by tags)."""
    selected_for_build = get_machines_for_build(
        Flake(str(test_flake_with_core.path)),
        explicit_names=explicit_names,
        filter_tags=filter_tags,
    )
    names = [m.name for m in selected_for_build]

    assert sorted(names) == sorted(expected_names)


@pytest.mark.with_core
def test_get_machines_for_build_nonexistent_machine(
    test_flake_with_core: FlakeForTest,
) -> None:
    """Test that building nonexistent machine raises error with helpful message."""
    with pytest.raises(ClanError) as exc_info:
        get_machines_for_build(
            Flake(str(test_flake_with_core.path)),
            explicit_names=["nonexistent-machine"],
            filter_tags=[],
        )

    error_message = str(exc_info.value)
    assert "nonexistent-machine" in error_message
    assert "not found" in error_message.lower()


def test_build_command_no_flake(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that build command fails gracefully when not in a flake directory."""
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ClanError):
        cli.run(["machines", "build", "machine1"])
