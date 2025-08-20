# Functions to test
from copy import deepcopy
from typing import Any

import pytest

from clan_lib.errors import ClanError
from clan_lib.persist.util import (
    calc_patches,
    delete_by_path,
    determine_writeability,
    list_difference,
    merge_objects,
    path_match,
    set_value_by_path,
)


@pytest.mark.parametrize(
    ("path", "whitelist", "expected"),
    [
        # Exact matches
        (["a", "b", "c"], [["a", "b", "c"]], True),
        (["a", "b"], [["a", "b"]], True),
        ([], [[]], True),
        # Wildcard matches
        (["a", "b", "c"], [["a", "*", "c"]], True),
        (["a", "x", "c"], [["a", "*", "c"]], True),
        (["a", "b", "c"], [["*", "b", "c"]], True),
        (["a", "b", "c"], [["a", "b", "*"]], True),
        (["a", "b", "c"], [["*", "*", "*"]], True),
        # Multiple patterns - one matches
        (["a", "b", "c"], [["x", "y", "z"], ["a", "*", "c"]], True),
        (["x", "y", "z"], [["a", "*", "c"], ["x", "y", "z"]], True),
        # Length mismatch
        (["a", "b", "c"], [["a", "b"]], False),
        (["a", "b"], [["a", "b", "c"]], False),
        # Non-matching
        (["a", "b", "c"], [["a", "b", "x"]], False),
        (["a", "b", "c"], [["a", "x", "x"]], False),
        (["a", "b", "c"], [["x", "x", "x"]], False),
        # Empty whitelist
        (["a"], [], False),
        # Wildcards and exact mixed
        (
            ["instances", "inst1", "roles", "roleA", "settings"],
            [["instances", "*", "roles", "*", "settings"]],
            True,
        ),
        # Partial wildcard - length mismatch should fail
        (
            ["instances", "inst1", "roles", "roleA"],
            [["instances", "*", "roles", "*", "settings"]],
            False,
        ),
        # Empty path, no patterns
        ([], [], False),
    ],
)
def test_path_match(
    path: list[str],
    whitelist: list[list[str]],
    expected: bool,
) -> None:
    assert path_match(path, whitelist) == expected


# --------- Patching tests ---------
def test_patch_nested() -> None:
    orig = {"a": 1, "b": {"a": 2.1, "b": 2.2}, "c": 3}

    set_value_by_path(orig, "b.b", "foo")

    # Should only update the nested value
    assert orig == {"a": 1, "b": {"a": 2.1, "b": "foo"}, "c": 3}


def test_patch_nested_dict() -> None:
    orig = {"a": 1, "b": {"a": 2.1, "b": 2.2}, "c": 3}

    # This should update the whole "b" dict
    # Which also removes all other keys
    set_value_by_path(orig, "b", {"b": "foo"})

    # Should only update the nested value
    assert orig == {"a": 1, "b": {"b": "foo"}, "c": 3}


def test_create_missing_paths() -> None:
    orig = {"a": 1}

    set_value_by_path(orig, "b.c", "foo")

    # Should only update the nested value
    assert orig == {"a": 1, "b": {"c": "foo"}}

    orig = {}
    set_value_by_path(orig, "a.b.c", "foo")

    assert orig == {"a": {"b": {"c": "foo"}}}


# --------- Write tests ---------
#


def test_write_simple() -> None:
    prios = {
        "foo": {
            "__prio": 100,  # <- writeable: "foo"
            "bar": {"__prio": 1000},  # <- writeable: mkDefault "foo.bar"
        },
    }

    default: dict = {"foo": {}}
    data: dict = {}
    res = determine_writeability(prios, default, data)

    assert res == {"writeable": {"foo", "foo.bar"}, "non_writeable": set({})}


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
        "writeable": {"foo", "foo.bar", "foo.bar.baz"},
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
        "non_writeable": {"foo", "foo.bar", "foo.bar.baz"},
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
        "writeable": {"foo"},
        "non_writeable": set(),
    }


def test_write_because_written() -> None:
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
        "writeable": {"foo", "foo.bar"},
        "non_writeable": {"foo.bar.baz", "foo.bar.foobar"},
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
        "writeable": {"foo", "foo.bar", "foo.bar.baz"},
        "non_writeable": {"foo.bar.foobar"},
    }


# --------- List unmerge tests ---------


def test_list_unmerge() -> None:
    all_machines = ["machineA", "machineB"]
    inventory = ["machineB"]

    nix_machines = list_difference(all_machines, inventory)
    assert nix_machines == ["machineA"]


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

    assert writeables == {"writeable": {"foo", "foo.bar"}, "non_writeable": {"foo.nix"}}

    update = {
        "foo": {
            "bar": "new value",  # <- user sets this value
            "nix": "this is set in nix",  # <- user didnt touch this value
            # If the user would have set this value, it would trigger an error
        },
    }
    patchset, _ = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {"foo.bar": "new value"}


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

    set_value_by_path(update, "foo.mimi", {})

    patchset, _ = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {"foo.mimi": {}}  # this is what gets persisted


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
        "writeable": {"foo.nested", "foo", "foo.bar", "foo.nested.x"},
        "non_writeable": {"foo.nix", "foo.nested.y"},
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
    patchset, _ = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {
        "foo.bar": "new value for bar",
        "foo.nested.x": "new value for x",
    }


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

    assert writeables == {"writeable": set(), "non_writeable": {"foo", "foo.bar"}}

    update = {
        "foo": {
            "bar": "new value",  # <- user sets this value
        },
    }
    with pytest.raises(ClanError) as error:
        calc_patches(data_disk, update, all_values=data_eval, writeables=writeables)

    assert "Key 'foo.bar' is not writeable." in str(error.value)


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

    assert writeables == {"writeable": {"foo"}, "non_writeable": set()}

    # Add "C" to the list
    update = {"foo": ["A", "B", "C"]}  # User wants to add "C"

    patchset, _ = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {"foo": ["B", "C"]}

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

    assert patchset == {"foo": []}


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

    assert writeables == {"writeable": {"foo"}, "non_writeable": set()}

    # Add "A" to the list
    update = {"foo": ["A", "B", "A"]}  # User wants to add duplicate "A"

    with pytest.raises(ClanError) as error:
        calc_patches(data_disk, update, all_values=data_eval, writeables=writeables)

    assert "Key 'foo' contains list duplicates: ['A']" in str(error.value)


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
    assert writeables == {"writeable": {"config", "enabled"}, "non_writeable": set()}

    update = deepcopy(data_eval)
    set_value_by_path(update, "config.foo", "foo")

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )
    assert patchset == {"config.foo": "foo"}
    assert delete_set == set()


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
    assert writeables == {"writeable": {"machines"}, "non_writeable": set()}

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
    assert delete_set == {"machines.bar"}


def test_update_mismatching_update_type() -> None:
    prios = {
        "foo": {
            "__prio": 100,  # <- writeable: "foo"
        },
    }

    data_eval = {"foo": ["A", "B"]}

    data_disk: dict = {}

    writeables = determine_writeability(prios, data_eval, data_disk)

    assert writeables == {"writeable": {"foo"}, "non_writeable": set()}

    # set foo to an int but it is a list
    update: dict = {"foo": 1}

    with pytest.raises(ClanError) as error:
        calc_patches(data_disk, update, all_values=data_eval, writeables=writeables)

    assert (
        "Type mismatch for key 'foo'. Cannot update <class 'list'> with <class 'int'>"
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

    assert writeables == {"writeable": {"foo"}, "non_writeable": set()}

    # remove all keys from foo
    update: dict = {"foo": {}}

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {"foo": {}}
    assert delete_set == {"foo.bar"}


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

    assert writeables == {"writeable": {"foo"}, "non_writeable": set()}

    # remove all keys from foo

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        writeables=writeables,
    )

    assert patchset == {}
    assert delete_set == {"foo.bar"}


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

    assert writeables == {"writeable": set(), "non_writeable": {"foo"}}

    # remove all keys from foo
    with pytest.raises(ClanError) as error:
        calc_patches(data_disk, update, all_values=data_eval, writeables=writeables)

    assert "is not writeable" in str(error.value)


def test_delete_atom() -> None:
    data = {"foo": {"bar": 1}}
    # Removes the key "foo.bar"
    # Returns the deleted key-value pair { "bar": 1 }
    entry = delete_by_path(data, "foo.bar")

    assert entry == {"bar": 1}
    assert data == {"foo": {}}


def test_delete_intermediate() -> None:
    data = {"a": {"b": {"c": {"d": 42}}}}
    # Removes "a.b.c.d"
    entry = delete_by_path(data, "a.b.c")

    assert entry == {"c": {"d": 42}}
    # Check all intermediate dictionaries remain intact
    assert data == {"a": {"b": {}}}


def test_delete_top_level() -> None:
    data = {"x": 100, "y": 200}
    # Deletes top-level key
    entry = delete_by_path(data, "x")
    assert entry == {"x": 100}
    assert data == {"y": 200}


def test_delete_key_not_found() -> None:
    data = {"foo": {"bar": 1}}
    # Trying to delete a non-existing key "foo.baz"
    with pytest.raises(KeyError) as excinfo:
        delete_by_path(data, "foo.baz")
    assert "Cannot delete. Path 'foo.baz'" in str(excinfo.value)
    # Data should remain unchanged
    assert data == {"foo": {"bar": 1}}


def test_delete_intermediate_not_dict() -> None:
    data = {"foo": "not a dict"}
    # Trying to go deeper into a non-dict value
    with pytest.raises(KeyError) as excinfo:
        delete_by_path(data, "foo.bar")
    assert "not found or not a dictionary" in str(excinfo.value)
    # Data should remain unchanged
    assert data == {"foo": "not a dict"}


def test_delete_empty_path() -> None:
    data = {"foo": {"bar": 1}}
    # Attempting to delete with an empty path
    with pytest.raises(KeyError) as excinfo:
        delete_by_path(data, "")
    # Depending on how you handle empty paths, you might raise an error or handle it differently.
    # If you do raise an error, check the message.
    assert "Cannot delete. Path is empty" in str(excinfo.value)
    assert data == {"foo": {"bar": 1}}


def test_delete_non_existent_path_deep() -> None:
    data = {"foo": {"bar": {"baz": 123}}}
    # non-existent deep path
    with pytest.raises(KeyError) as excinfo:
        delete_by_path(data, "foo.bar.qux")
    assert "not found" in str(excinfo.value)
    # Data remains unchanged
    assert data == {"foo": {"bar": {"baz": 123}}}


### Merge Objects Tests ###


def test_merge_objects_empty() -> None:
    obj1 = {}  # type: ignore
    obj2 = {}  # type: ignore

    merged = merge_objects(obj1, obj2)

    assert merged == {}


def test_merge_objects_basic() -> None:
    obj1 = {"a": 1, "b": 2}
    obj2 = {"b": 3, "c": 4}

    merged = merge_objects(obj1, obj2)

    assert merged == {"a": 1, "b": 3, "c": 4}


def test_merge_objects_simple() -> None:
    obj1 = {"a": 1}
    obj2 = {"a": None}

    # merge_objects should update obj2 with obj1
    # Set a value to None
    merged_order = merge_objects(obj1, obj2)

    assert merged_order == {"a": None}

    # Test reverse merge
    # Set a value from None to 1
    merged_reverse = merge_objects(obj2, obj1)

    assert merged_reverse == {"a": 1}


def test_merge_none_to_value() -> None:
    obj1 = {
        "a": None,
    }
    obj2 = {"a": {"b": 1}}

    merged_obj = merge_objects(obj1, obj2)
    assert merged_obj == {"a": {"b": 1}}

    obj3 = {"a": [1, 2, 3]}
    merged_list = merge_objects(obj1, obj3)
    assert merged_list == {"a": [1, 2, 3]}

    obj4 = {"a": 1}
    merged_int = merge_objects(obj1, obj4)
    assert merged_int == {"a": 1}

    obj5 = {"a": "test"}
    merged_str = merge_objects(obj1, obj5)
    assert merged_str == {"a": "test"}

    obj6 = {"a": True}
    merged_bool = merge_objects(obj1, obj6)
    assert merged_bool == {"a": True}


def test_merge_objects_value_to_none() -> None:
    obj1 = {"a": {"b": 1}}
    obj2 = {"a": None}

    merged_obj = merge_objects(obj1, obj2)
    assert merged_obj == {"a": None}

    obj3 = {"a": [1, 2, 3]}
    merged_list = merge_objects(obj3, obj2)
    assert merged_list == {"a": None}

    obj4 = {"a": 1}
    merged_int = merge_objects(obj4, obj2)
    assert merged_int == {"a": None}

    obj5 = {"a": "test"}
    merged_str = merge_objects(obj5, obj2)
    assert merged_str == {"a": None}

    obj6 = {"a": True}
    merged_bool = merge_objects(obj6, obj2)
    assert merged_bool == {"a": None}


def test_merge_objects_nested() -> None:
    obj1 = {"a": {"b": 1, "c": 2}, "d": 3}
    obj2 = {"a": {"b": 4}, "e": 5}

    merged = merge_objects(obj1, obj2)

    assert merged == {"a": {"b": 4, "c": 2}, "d": 3, "e": 5}


def test_merge_objects_lists() -> None:
    obj1 = {"a": [1, 2], "b": {"c": [3, 4]}}
    obj2 = {"a": [2, 3], "b": {"c": [4, 5]}}

    merged = merge_objects(obj1, obj2)

    # Lists get merged and deduplicated
    # Lists (get sorted, but that is not important)
    # Maybe we shouldn't sort them?
    assert merged == {"a": [1, 2, 3], "b": {"c": [3, 4, 5]}}


def test_merge_objects_unset_list_elements() -> None:
    obj1 = {"a": [1, 2], "b": {"c": [3, 4]}}
    obj2 = {"a": [], "b": {"c": [5]}}

    merged = merge_objects(obj1, obj2, merge_lists=False)

    # Lists get merged and deduplicated
    # None values are not removed
    assert merged == {"a": [], "b": {"c": [5]}}


def test_merge_objects_with_mismatching_nesting() -> None:
    obj1 = {"a": {"b": 1}, "c": 2}
    obj2 = {"a": 3}

    # Merging should raise an error because obj1 and obj2 have different nesting for 'a'
    with pytest.raises(ClanError) as excinfo:
        merge_objects(obj1, obj2)

    assert "Type mismatch for key 'a'" in str(excinfo.value)
