from copy import deepcopy
from typing import Any

import pytest

from clan_lib.errors import ClanError
from clan_lib.persist.static_data import (
    calc_patches,
    calculate_static_data,
    determine_writeability,
    flatten_data_structured,
    set_value_by_path_tuple,
)
from clan_lib.persist.util import delete_by_path, set_value_by_path


def test_flatten_data_structured() -> None:
    data = {
        "name": "example",
        "settings": {
            "optionA": True,
            "optionB": {
                "subOption1": 10,
                "subOption2": 20,
            },
            "emptyDict": {},
        },
        "listSetting": [1, 2, 3],
    }

    expected_flat = {
        ("name",): "example",
        ("settings", "optionA"): True,
        ("settings", "optionB", "subOption1"): 10,
        ("settings", "optionB", "subOption2"): 20,
        ("settings", "emptyDict"): {},
        ("listSetting",): [1, 2, 3],
    }

    flattened = flatten_data_structured(data)
    assert flattened == expected_flat


def test_flatten_data_structured_empty() -> None:
    data: dict = {}
    expected_flat: dict = {}
    flattened = flatten_data_structured(data)
    assert flattened == expected_flat


def test_flatten_data_structured_nested_empty() -> None:
    data: dict = {
        "level1": {
            "level2": {
                "level3": {},
            },
        },
    }
    expected_flat: dict = {
        ("level1", "level2", "level3"): {},
    }
    flattened = flatten_data_structured(data)
    assert flattened == expected_flat


def test_flatten_data_dot_in_keys() -> None:
    data = {
        "key.foo": "value1",
        "key": {
            "foo": "value2",
        },
    }
    expected_flat = {
        ("key.foo",): "value1",
        ("key", "foo"): "value2",
    }
    flattened = flatten_data_structured(data)
    assert flattened == expected_flat


def test_calculate_static_data_basic() -> None:
    all_values = {
        "name": "example",
        "version": 1,
        "settings": {
            "optionA": True,
            "optionB": False,
            "listSetting": [1, 2, 3, 4],
        },
        "staticOnly": "staticValue",
    }
    persisted = {
        "name": "example",
        "version": 1,
        "settings": {
            "optionA": True,
            "listSetting": [2, 3],
        },
    }

    expected_static = {
        ("settings", "optionB"): False,
        ("settings", "listSetting"): [1, 4],
        ("staticOnly",): "staticValue",
    }

    static_data = calculate_static_data(all_values, persisted)
    assert static_data == expected_static


def test_calculate_static_data_no_static() -> None:
    all_values = {
        "name": "example",
        "version": 1,
        "settings": {
            "optionA": True,
            "listSetting": [1, 2, 3],
        },
    }
    persisted = {
        "name": "example",
        "version": 1,
        "settings": {
            "optionA": True,
            "listSetting": [1, 2, 3],
        },
    }

    expected_static: dict = {}

    static_data = calculate_static_data(all_values, persisted)
    assert static_data == expected_static


def test_calculate_static_data_all_static() -> None:
    all_values = {
        "name": "example",
        "version": 1,
        "settings": {
            "optionA": True,
            "listSetting": [1, 2, 3],
        },
        "staticOnly": "staticValue",
    }
    persisted: dict = {}

    expected_static = {
        ("name",): "example",
        ("version",): 1,
        ("settings", "optionA"): True,
        ("settings", "listSetting"): [1, 2, 3],
        ("staticOnly",): "staticValue",
    }

    static_data = calculate_static_data(all_values, persisted)
    assert static_data == expected_static


def test_calculate_static_data_empty_all_values() -> None:
    # This should never happen in practice, but we test it for completeness.
    # Maybe this should emit a warning in the future?
    all_values: dict = {}
    persisted = {
        "name": "example",
        "version": 1,
    }

    expected_static: dict = {}

    static_data = calculate_static_data(all_values, persisted)
    assert static_data == expected_static


def test_calculate_nested_dicts() -> None:
    all_values = {
        "level1": {
            "level2": {
                "staticKey": "staticValue",
                "persistedKey": "persistedValue",
            },
            "anotherStatic": 42,
        },
        "topLevelStatic": True,
    }
    persisted = {
        "level1": {
            "level2": {
                "persistedKey": "persistedValue",
            },
        },
    }

    expected_static = {
        ("level1", "level2", "staticKey"): "staticValue",
        ("level1", "anotherStatic"): 42,
        ("topLevelStatic",): True,
    }

    static_data = calculate_static_data(all_values, persisted)
    assert static_data == expected_static


def test_dot_in_keys() -> None:
    all_values = {
        "key.foo": "staticValue",
        "key": {
            "foo": "anotherStaticValue",
        },
    }
    persisted: dict = {}

    expected_static = {
        ("key.foo",): "staticValue",
        ("key", "foo"): "anotherStaticValue",
    }

    static_data = calculate_static_data(all_values, persisted)

    assert static_data == expected_static


def test_write_simple() -> None:
    prios = {
        "foo": {
            "__prio": 100,  # <- writeable: "foo"
            "bar": {"__prio": 1000},  # <- writeable: mkDefault "foo.bar"
        },
        "foo.bar": {"__prio": 1000},
    }

    default: dict = {"foo": {}}
    data: dict = {}
    res = determine_writeability(prios, default, data)

    assert res == {
        "writeable": {("foo", "bar"), ("foo",), ("foo.bar",)},
        "non_writeable": set(),
    }


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
    res = determine_writeability(prios, {"foo": {"bar": {}}}, data)

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
    res = determine_writeability(prios, {}, data)

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
    res = determine_writeability(prios, default, data)
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
    res = determine_writeability(prios, {"foo": {"bar": {}}}, {})
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
    res = determine_writeability(prios, {}, data)
    assert res == {
        "writeable": {("foo",), ("foo", "bar"), ("foo", "bar", "baz")},
        "non_writeable": {("foo", "bar", "foobar")},
    }


# --------- Write tests ---------


def test_update_simple() -> None:
    prios = {
        "foo": {
            "__prio": 100,  # <- writeable: "foo"
            "bar": {"__prio": 1000},  # <- writeable: mkDefault "foo.bar"
            "nix": {"__prio": 100},  # <- non writeable: "foo.bar" (defined in nix)
        },
    }

    data_eval = {"foo": {"bar": "baz", "nix": "this is set in nix"}}

    data_disk: dict = {}

    writeables = determine_writeability(prios, data_eval, data_disk)

    assert writeables == {
        "writeable": {("foo",), ("foo", "bar")},
        "non_writeable": {("foo", "nix")},
    }
    update = {
        "foo": {
            "bar": "new value",  # <- user sets this value
            # If the user would have set this value, it would trigger an error
            "nix": "this is set in nix",  # <- user didnt touch this value
        },
    }
    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {("foo", "bar"): "new value"}
    assert delete_set == set()


def test_update_add_empty_dict() -> None:
    prios = {
        "foo": {
            "__prio": 100,  # <- writeable: "foo"
            "nix": {"__prio": 100},  # <- non writeable: "foo.nix" (defined in nix)
        },
    }

    data_eval: dict = {"foo": {"nix": {}}}

    data_disk: dict = {}

    writeables = determine_writeability(prios, data_eval, data_disk)

    update = deepcopy(data_eval)

    set_value_by_path_tuple(update, ("foo", "mimi"), {})

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {("foo", "mimi"): {}}  # this is what gets persisted
    assert delete_set == set()


def test_update_many() -> None:
    prios = {
        "foo": {
            "__prio": 100,  # <- writeable: "foo"
            "bar": {"__prio": 100},  # <-
            "nix": {"__prio": 100},  # <- non writeable: "foo.nix" (defined in nix)
            "nested": {
                "__prio": 100,
                "x": {"__prio": 100},  # <- writeable: "foo.nested.x"
                "y": {"__prio": 100},  # <- non-writeable: "foo.nested.y"
            },
        },
    }

    data_eval = {
        "foo": {
            "bar": "baz",
            "nix": "this is set in nix",
            "nested": {"x": "x", "y": "y"},
        },
    }

    data_disk = {"foo": {"bar": "baz", "nested": {"x": "x"}}}

    writeables = determine_writeability(prios, data_eval, data_disk)

    assert writeables == {
        "writeable": {
            ("foo",),
            ("foo", "bar"),
            ("foo", "nested"),
            ("foo", "nested", "x"),
        },
        "non_writeable": {("foo", "nix"), ("foo", "nested", "y")},
    }

    update = {
        "foo": {
            "bar": "new value for bar",  # <- user sets this value
            "nix": "this is set in nix",  # <- user cannot set this value
            "nested": {
                "x": "new value for x",  # <- user sets this value
                "y": "y",  # <- user cannot set this value
            },
        },
    }
    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {
        ("foo", "bar"): "new value for bar",
        ("foo", "nested", "x"): "new value for x",
    }
    assert delete_set == set()


def test_update_parent_non_writeable() -> None:
    prios = {
        "foo": {
            "__prio": 50,  # <- non-writeable: "foo"
            "bar": {"__prio": 1000},  # <- writeable: mkDefault "foo.bar"
        },
    }

    data_eval = {
        "foo": {
            "bar": "baz",
        },
    }

    data_disk = {
        "foo": {
            "bar": "baz",
        },
    }

    writeables = determine_writeability(prios, data_eval, data_disk)

    assert writeables == {
        "writeable": set(),
        "non_writeable": {("foo",), ("foo", "bar")},
    }

    update = {
        "foo": {
            "bar": "new value",  # <- user sets this value
        },
    }
    with pytest.raises(ClanError) as error:
        calc_patches(data_disk, update, all_values=data_eval, writeables=writeables)

    assert "Path 'foo.bar' is readonly." in str(error.value)


def test_remove_non_writable_attrs() -> None:
    prios = {
        "foo": {
            "__prio": 100,  # <- writeable: "foo"
        },
    }

    data_eval: dict = {"foo": {"bar": {}, "baz": {}}}

    data_disk: dict = {}

    writeables = determine_writeability(prios, data_eval, data_disk)

    update: dict = {
        "foo": {
            "bar": {},  # <- user leaves this value
            # User removed "baz"
        },
    }

    with pytest.raises(ClanError) as error:
        calc_patches(data_disk, update, all_values=data_eval, writeables=writeables)

    assert "Cannot delete path 'foo.baz'" in str(error.value)


def test_update_list() -> None:
    prios = {
        "foo": {
            "__prio": 100,  # <- writeable: "foo"
        },
    }

    data_eval = {
        #  [ "A" ]  is defined in nix.
        "foo": ["A", "B"],
    }

    data_disk = {"foo": ["B"]}

    writeables = determine_writeability(prios, data_eval, data_disk)

    assert writeables == {"writeable": {("foo",)}, "non_writeable": set()}

    # Add "C" to the list
    update = {"foo": ["A", "B", "C"]}  # User wants to add "C"

    patchset, _ = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {("foo",): ["B", "C"]}

    # "foo": ["A", "B"]
    # Remove "B" from the list
    # Expected is [ ] because ["A"] is defined in nix
    update = {"foo": ["A"]}  # User wants to remove "B"

    patchset, _ = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {("foo",): []}


def test_update_list_duplicates() -> None:
    prios = {
        "foo": {
            "__prio": 100,  # <- writeable: "foo"
        },
    }

    data_eval = {
        #  [ "A" ]  is defined in nix.
        "foo": ["A", "B"],
    }

    data_disk = {"foo": ["B"]}

    writeables = determine_writeability(prios, data_eval, data_disk)

    assert writeables == {"writeable": {("foo",)}, "non_writeable": set()}

    # Add "A" to the list
    update = {"foo": ["A", "B", "A"]}  # User wants to add duplicate "A"

    with pytest.raises(ClanError) as error:
        calc_patches(data_disk, update, all_values=data_eval, writeables=writeables)

    assert "Path 'foo' contains list duplicates: ['A']" in str(error.value)


def test_dont_persist_defaults() -> None:
    """Default values should not be persisted to disk if not explicitly requested by the user."""
    prios = {
        "enabled": {"__prio": 1500},
        "config": {"__prio": 100},
    }
    data_eval = {
        "enabled": True,
        "config": {"foo": "bar"},
    }
    data_disk: dict[str, Any] = {}
    writeables = determine_writeability(prios, data_eval, data_disk)
    assert writeables == {
        "writeable": {("config",), ("enabled",)},
        "non_writeable": set(),
    }

    update = deepcopy(data_eval)
    set_value_by_path(update, "config.foo", "foo")

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )
    assert patchset == {("config", "foo"): "foo"}
    assert delete_set == set()


def test_set_null() -> None:
    data_eval: dict = {
        "foo": {},
        "bar": {},
    }
    data_disk = data_eval

    # User set Foo to null
    # User deleted bar
    update = {"foo": None}

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=determine_writeability(
            {"__prio": 100, "foo": {"__prio": 100}},
            data_eval,
            data_disk,
        ),
    )
    assert patchset == {("foo",): None}
    assert delete_set == {("bar",)}


def test_machine_delete() -> None:
    prios = {
        "machines": {"__prio": 100},
    }
    data_eval = {
        "machines": {
            "foo": {"name": "foo"},
            "bar": {"name": "bar"},
            "naz": {"name": "naz"},
        },
    }
    data_disk = data_eval

    writeables = determine_writeability(prios, data_eval, data_disk)
    assert writeables == {"writeable": {("machines",)}, "non_writeable": set()}

    # Delete machine "bar"  from the inventory
    update = deepcopy(data_eval)
    delete_by_path(update, "machines.bar")

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {}
    assert delete_set == {("machines", "bar")}


def test_update_mismatching_update_type() -> None:
    prios = {
        "foo": {
            "__prio": 100,  # <- writeable: "foo"
        },
    }

    data_eval = {"foo": ["A", "B"]}

    data_disk: dict = {}

    writeables = determine_writeability(prios, data_eval, data_disk)

    assert writeables == {"writeable": {("foo",)}, "non_writeable": set()}

    # set foo to an int but it is a list
    update: dict = {"foo": 1}

    with pytest.raises(ClanError) as error:
        calc_patches(data_disk, update, all_values=data_eval, writeables=writeables)

    assert (
        "Type mismatch for path 'foo'. Cannot update <class 'list'> with <class 'int'>"
        in str(error.value)
    )


def test_delete_key() -> None:
    prios = {
        "foo": {
            "__prio": 100,  # <- writeable: "foo"
        },
    }

    data_eval = {"foo": {"bar": "baz"}}

    data_disk = data_eval

    writeables = determine_writeability(prios, data_eval, data_disk)

    assert writeables == {"writeable": {("foo",)}, "non_writeable": set()}

    # remove all keys from foo
    update: dict = {"foo": {}}

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {("foo",): {}}
    assert delete_set == {("foo", "bar")}


def test_delete_key_intermediate() -> None:
    prios = {
        "foo": {
            "__prio": 100,
        },
    }

    data_eval = {
        "foo": {
            # Remove the key "bar"
            "bar": {"name": "bar", "info": "info", "other": ["a", "b"]},
            # Leave the key "other"
            "other": {"name": "other", "info": "info", "other": ["a", "b"]},
        },
    }
    update: dict = {
        "foo": {"other": {"name": "other", "info": "info", "other": ["a", "b"]}},
    }

    data_disk = data_eval

    writeables = determine_writeability(prios, data_eval, data_disk)

    assert writeables == {"writeable": {("foo",)}, "non_writeable": set()}

    # remove all keys from foo

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {}
    assert delete_set == {("foo", "bar")}


def test_delete_key_non_writeable() -> None:
    prios = {
        "foo": {
            "__prio": 50,
        },
    }

    data_eval = {
        "foo": {
            # Remove the key "bar"
            "bar": {"name": "bar", "info": "info", "other": ["a", "b"]},
        },
    }
    update: dict = {"foo": {}}

    data_disk = data_eval

    writeables = determine_writeability(prios, data_eval, data_disk)

    assert writeables == {"writeable": set(), "non_writeable": {("foo",)}}

    # remove all keys from foo
    with pytest.raises(ClanError) as error:
        calc_patches(data_disk, update, all_values=data_eval, writeables=writeables)

    assert "Path 'foo' is readonly." in str(error.value)
