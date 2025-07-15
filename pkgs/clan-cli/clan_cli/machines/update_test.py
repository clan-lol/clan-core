from pathlib import Path

import pytest
from clan_lib.errors import ClanError
from clan_lib.flake import Flake

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
                }"""
            },
            ["jon"],  # explizit names
            [],  # filter tags
            ["jon"],  # expected
        )
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=["test_flake_with_core"],
)
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
                }"""
            },
            [],  # explizit names
            ["foo"],  # filter tags
            ["jon", "sara"],  # expected
        )
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=["test_flake_with_core"],
)
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
                }"""
            },
            ["sara"],  # explizit names
            ["foo"],  # filter tags
            ["sara"],  # expected
        )
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=["test_flake_with_core"],
)
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
                }"""
            },
            [],  # no explizit names
            [],  # no filter tags
            ["jon", "sara", "vm1", "vm2"],  # all machines
        ),
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=["test_flake_with_core"],
)
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
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    with pytest.raises(ClanError):
        cli.run(["machines", "update", "machine1"])


# TODO: Add more tests for requireExplicitUpdate
