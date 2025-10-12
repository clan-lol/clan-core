from collections.abc import Callable
from typing import TYPE_CHECKING, cast

import pytest

from clan_lib.flake.flake import Flake
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.write_rules import PersistenceAttribute, compute_attribute_map

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

    res = compute_attribute_map(prios, data_eval, {})

    # We should be able to write to these top-level keys
    assert PersistenceAttribute.WRITE in res[("machines",)]
    assert PersistenceAttribute.WRITE in res[("instances",)]
    assert PersistenceAttribute.WRITE in res[("meta",)]

    # # Managed by nix
    assert PersistenceAttribute.WRITE not in res[("assertions",)]
    assert PersistenceAttribute.READONLY in res[("assertions",)]


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
    res = compute_attribute_map(prios, default, data)

    assert res == {
        ("foo",): {PersistenceAttribute.WRITE},
        # Can be deleted, because it has a parent.
        # The parent doesnt set "total", so we assume its not total.
        ("foo", "bar"): {PersistenceAttribute.WRITE, PersistenceAttribute.DELETE},
        ("foo.bar",): {PersistenceAttribute.WRITE},
    }


# ---- Compatibility tests ---- #


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
    res = compute_attribute_map(prios, {"foo": {"bar": {}}}, data)

    assert res == {
        ("foo",): {PersistenceAttribute.WRITE},
        ("foo", "bar"): {PersistenceAttribute.WRITE, PersistenceAttribute.DELETE},
        ("foo", "bar", "baz"): {
            PersistenceAttribute.WRITE,
            PersistenceAttribute.DELETE,
        },
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
    res = compute_attribute_map(prios, {}, data)

    assert res == {
        ("foo",): {PersistenceAttribute.READONLY},
        ("foo", "bar"): {PersistenceAttribute.READONLY},
        ("foo", "bar", "baz"): {PersistenceAttribute.READONLY},
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
    res = compute_attribute_map(prios, default, data)

    assert res == {
        ("foo",): {PersistenceAttribute.WRITE},
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
    res = compute_attribute_map(prios, {"foo": {"bar": {}}}, {})

    assert res == {
        ("foo",): {PersistenceAttribute.WRITE},
        ("foo", "bar"): {PersistenceAttribute.WRITE, PersistenceAttribute.DELETE},
        ("foo", "bar", "baz"): {
            PersistenceAttribute.READONLY,
        },
        ("foo", "bar", "foobar"): {
            PersistenceAttribute.READONLY,
        },
    }
    data: dict = {
        "foo": {
            "bar": {
                "baz": "foo",  # <- written. Since we created the data, we know we can write to it
            },
        },
    }
    res = compute_attribute_map(prios, {}, data)

    assert res[("foo", "bar", "baz")] == {
        PersistenceAttribute.WRITE,
        PersistenceAttribute.DELETE,
    }


### --- NEW API ---


def test_static_object() -> None:
    introspection = {
        "foo": {
            "__this": {
                "files": ["inventory.json", "<unknown-file>"],
                "prio": 100,
                "total": False,
            },
            "a": {
                "__this": {
                    "files": ["inventory.json", "<unknown-file>"],
                    "prio": 100,
                    "total": False,
                },
                "c": {
                    "__this": {
                        "files": ["inventory.json", "<unknown-file>"],
                        "prio": 100,
                        "total": False,
                    },
                    "bar": {
                        "__this": {
                            "files": ["inventory.json"],
                            "prio": 100,
                            "total": False,
                        }
                    },
                },
            },
        }
    }
    data_eval: dict = {"foo": {"a": {"c": {"bar": 1}}}}
    persisted: dict = {"foo": {"a": {"c": {"bar": 1}}}}

    res = compute_attribute_map(introspection, data_eval, persisted)
    assert res == {
        # We can extend "foo", "foo.a", "foo.a.c"
        # That means the user could define "foo.b"
        # But they cannot delete "foo.a" or its static subkeys "foo.a.c"
        ("foo",): {PersistenceAttribute.WRITE},
        ("foo", "a"): {PersistenceAttribute.WRITE},
        ("foo", "a", "c"): {PersistenceAttribute.WRITE},
        # We can delete "bar"
        ("foo", "a", "c", "bar"): {
            PersistenceAttribute.DELETE,
            PersistenceAttribute.WRITE,
        },
    }


def test_attributes_totality() -> None:
    introspection = {
        "foo": {
            "__this": {
                "files": ["inventory.json"],
                "prio": 100,
                "total": True,
            },
            "a": {  # Cannot delete "a" because parent is total
                "__this": {
                    "files": ["inventory.json", "<unknown-file>"],
                    "prio": 100,
                    "total": False,
                },
            },
        }
    }
    data_eval: dict = {"foo": {"a": {}}}
    persisted: dict = {"foo": {"a": {}}}

    res = compute_attribute_map(introspection, data_eval, persisted)

    assert res == {
        ("foo",): {PersistenceAttribute.WRITE},
        ("foo", "a"): {PersistenceAttribute.WRITE},
    }
