from pathlib import Path

import pytest
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.update import _build_darwin_rebuild_cmd

from clan_cli.machines.update import get_machines_for_update
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
            ["jon"],  # explicit names
            [],  # filter tags
            ["jon"],  # expected
        ),
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=["test_flake_with_core"],
)
@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_get_machines_for_update_single_name(
    test_flake_with_core: FlakeForTest,
    explicit_names: list[str],
    filter_tags: list[str],
    expected_names: list[str],
) -> None:
    selected_for_update = get_machines_for_update(
        Flake(str(test_flake_with_core.path)),
        explicit_names=explicit_names,
        filter_tags=filter_tags,
    )
    names = [m.name for m in selected_for_update]

    print(explicit_names, filter_tags)
    assert names == expected_names


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
            [],  # explicit names
            ["foo"],  # filter tags
            ["jon", "sara"],  # expected
        ),
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=["test_flake_with_core"],
)
@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_get_machines_for_update_tags(
    test_flake_with_core: FlakeForTest,
    explicit_names: list[str],
    filter_tags: list[str],
    expected_names: list[str],
) -> None:
    selected_for_update = get_machines_for_update(
        Flake(str(test_flake_with_core.path)),
        explicit_names=explicit_names,
        filter_tags=filter_tags,
    )
    names = [m.name for m in selected_for_update]

    print(explicit_names, filter_tags)
    assert names == expected_names


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
            ["sara"],  # explicit names
            ["foo"],  # filter tags
            ["sara"],  # expected
        ),
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=["test_flake_with_core"],
)
@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_get_machines_for_update_tags_and_name(
    test_flake_with_core: FlakeForTest,
    explicit_names: list[str],
    filter_tags: list[str],
    expected_names: list[str],
) -> None:
    selected_for_update = get_machines_for_update(
        Flake(str(test_flake_with_core.path)),
        explicit_names=explicit_names,
        filter_tags=filter_tags,
    )
    names = [m.name for m in selected_for_update]

    print(explicit_names, filter_tags)
    assert names == expected_names


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
            [],  # no explicit names
            [],  # no filter tags
            ["jon", "sara", "vm1", "vm2"],  # all machines
        ),
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=["test_flake_with_core"],
)
@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_get_machines_for_update_implicit_all(
    test_flake_with_core: FlakeForTest,
    explicit_names: list[str],
    filter_tags: list[str],
    expected_names: list[str],
) -> None:
    selected_for_update = get_machines_for_update(
        Flake(str(test_flake_with_core.path)),
        explicit_names=explicit_names,
        filter_tags=filter_tags,
    )
    names = [m.name for m in selected_for_update]

    print(explicit_names, filter_tags)
    assert names == expected_names


def test_update_command_no_flake(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ClanError):
        cli.run(["machines", "update", "machine1"])


def test_darwin_rebuild_cmd_no_literal_quotes() -> None:
    """Regression: flake fragment must not contain literal quotes.

    Literal quotes around the machine name (e.g. ``#"emily"``) cause
    darwin-rebuild to fail because Nix cannot resolve the quoted attribute path.
    """
    cmd = _build_darwin_rebuild_cmd(
        machine_name="emily",
        flake_store_path="/nix/store/abc123-source",
        nix_options=["--show-trace"],
    )

    flake_arg = cmd[cmd.index("--flake") + 1]

    assert flake_arg == "/nix/store/abc123-source#emily"
    assert '"' not in flake_arg
    assert "'" not in flake_arg


def test_darwin_rebuild_cmd_structure() -> None:
    """The returned command has the expected shape."""
    cmd = _build_darwin_rebuild_cmd(
        machine_name="my-mac",
        flake_store_path="/nix/store/xyz-source",
        nix_options=["-L", "--option", "keep-going", "true"],
    )

    assert cmd[0] == "/run/current-system/sw/bin/darwin-rebuild"
    assert cmd[1] == "switch"
    assert "-L" in cmd
    assert cmd[-2] == "--flake"
    assert cmd[-1] == "/nix/store/xyz-source#my-mac"


# TODO: Add more tests for requireExplicitUpdate
