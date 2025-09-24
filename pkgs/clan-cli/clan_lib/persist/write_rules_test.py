from collections.abc import Callable
from typing import TYPE_CHECKING, cast

import pytest

from clan_lib.flake.flake import Flake
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.write_rules import compute_write_map

if TYPE_CHECKING:
    from clan_lib.nix_models.clan import Clan


# Integration test
@pytest.mark.with_core
def test_write_integration(clan_flake: Callable[..., Flake]) -> None:
    clan_nix: Clan = {}
    flake = clan_flake(clan_nix)
    inventory_store = InventoryStore(flake)
    # downcast into a dict
    data_eval = cast("dict", inventory_store.read())
    prios = flake.select("clanInternals.inventoryClass.introspection")

    res = compute_write_map(prios, data_eval, {})

    # We should be able to write to these top-level keys
    assert ("machines",) in res["writeable"]
    assert ("instances",) in res["writeable"]
    assert ("meta",) in res["writeable"]

    # Managed by nix
    assert ("assertions",) in res["non_writeable"]


# New style __this.prio


def test_write_simple() -> None:
    prios = {
        "foo": {
            "__this": {
                "prio": 100,  # <- writeable: "foo"
            },
            "bar": {"__this": {"prio": 1000}},  # <- writeable: mkDefault "foo.bar"
        },
        "foo.bar": {"__this": {"prio": 1000}},
    }

    default: dict = {"foo": {}}
    data: dict = {}
    res = compute_write_map(prios, default, data)

    assert res == {
        "writeable": {("foo", "bar"), ("foo",), ("foo.bar",)},
        "non_writeable": set(),
    }


# Compatibility test for old __prio style


def test_write_inherited() -> None:
    prios = {
        "foo": {
            "__prio": 100,  # <- writeable: "foo"
            "bar": {
                # Inherits prio from parent <- writeable: "foo.bar"
                "baz": {"__prio": 1000},  # <- writeable: "foo.bar.baz"
            },
        },
    }

    data: dict = {}
    res = compute_write_map(prios, {"foo": {"bar": {}}}, data)

    assert res == {
        "writeable": {("foo",), ("foo", "bar"), ("foo", "bar", "baz")},
        "non_writeable": set(),
    }


def test_non_write_inherited() -> None:
    prios = {
        "foo": {
            "__prio": 50,  # <- non writeable: mkForce "foo" = {...}
            "bar": {
                # Inherits prio from parent <- non writeable
                "baz": {"__prio": 1000},  # <- non writeable: mkDefault "foo.bar.baz"
            },
        },
    }

    data: dict = {}
    res = compute_write_map(prios, {}, data)

    assert res == {
        "writeable": set(),
        "non_writeable": {("foo",), ("foo", "bar", "baz"), ("foo", "bar")},
    }


def test_write_list() -> None:
    prios = {
        "foo": {
            "__prio": 100,
        },
    }

    data: dict = {}
    default: dict = {
        "foo": [
            "a",
            "b",
        ],  # <- writeable: because lists are merged. Filtering out nix-values comes later
    }
    res = compute_write_map(prios, default, data)
    assert res == {
        "writeable": {("foo",)},
        "non_writeable": set(),
    }


def test_write_because_written() -> None:
    # This test is essential to allow removing data that was previously written.
    # It may also have the weird effect, that somebody can change data, but others cannot.
    # But this might be acceptable, since its rare minority edge-case.
    prios = {
        "foo": {
            "__prio": 100,  # <- writeable: "foo"
            "bar": {
                # Inherits prio from parent <- writeable
                "baz": {"__prio": 100},  # <- non writeable usually
                "foobar": {"__prio": 100},  # <- non writeable
            },
        },
    }

    # Given the following data. {}
    # Check that the non-writeable paths are correct.
    res = compute_write_map(prios, {"foo": {"bar": {}}}, {})
    assert res == {
        "writeable": {("foo",), ("foo", "bar")},
        "non_writeable": {("foo", "bar", "baz"), ("foo", "bar", "foobar")},
    }

    data: dict = {
        "foo": {
            "bar": {
                "baz": "foo",  # <- written. Since we created the data, we know we can write to it
            },
        },
    }
    res = compute_write_map(prios, {}, data)
    assert res == {
        "writeable": {("foo",), ("foo", "bar"), ("foo", "bar", "baz")},
        "non_writeable": {("foo", "bar", "foobar")},
    }
