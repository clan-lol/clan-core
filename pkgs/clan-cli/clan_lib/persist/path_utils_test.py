import pytest

from clan_lib.persist.path_utils import (
    delete_by_path,
    flatten_data_structured,
    list_difference,
    path_match,
    set_value_by_path,
)

# --------- path_match ---------


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


# --------- set_value_by_path ---------


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


# ----  delete_by_path ----


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
    # Trying to delete a non-existing key "foo.baz" - should return empty dict
    result = delete_by_path(data, "foo.baz")
    assert result == {}
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
    # non-existent deep path - should return empty dict
    result = delete_by_path(data, "foo.bar.qux")
    assert result == {}
    # Data remains unchanged
    assert data == {"foo": {"bar": {"baz": 123}}}


# --- list_difference ---


def test_list_unmerge() -> None:
    all_machines = ["machineA", "machineB"]
    inventory = ["machineB"]

    nix_machines = list_difference(all_machines, inventory)
    assert nix_machines == ["machineA"]


# --- flatten_data_structured ---


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
