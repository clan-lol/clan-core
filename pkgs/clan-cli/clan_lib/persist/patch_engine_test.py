from copy import deepcopy
from typing import Any

import pytest

from clan_lib.errors import ClanError
from clan_lib.persist.patch_engine import (
    calc_patches,
    merge_objects,
)
from clan_lib.persist.path_utils import (
    delete_by_path,
    set_value_by_path,
    set_value_by_path_tuple,
)
from clan_lib.persist.write_rules import (
    PersistenceAttribute,
    compute_attribute_persistence,
)


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

    attribute_props = compute_attribute_persistence(prios, data_eval, data_disk)

    assert attribute_props == {
        ("foo",): {PersistenceAttribute.WRITE},
        ("foo", "bar"): {PersistenceAttribute.WRITE, PersistenceAttribute.DELETE},
        ("foo", "nix"): {PersistenceAttribute.READONLY},
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
        attribute_props=attribute_props,
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

    writeables = compute_attribute_persistence(prios, data_eval, data_disk)

    update = deepcopy(data_eval)

    set_value_by_path_tuple(update, ("foo", "mimi"), {})

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        attribute_props=writeables,
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

    attribute_props = compute_attribute_persistence(prios, data_eval, data_disk)

    assert attribute_props == {
        ("foo",): {PersistenceAttribute.WRITE},
        ("foo", "bar"): {PersistenceAttribute.WRITE, PersistenceAttribute.DELETE},
        ("foo", "nested"): {PersistenceAttribute.WRITE, PersistenceAttribute.DELETE},
        ("foo", "nested", "x"): {
            PersistenceAttribute.WRITE,
            PersistenceAttribute.DELETE,
        },
        # Readonly
        ("foo", "nix"): {PersistenceAttribute.READONLY},
        ("foo", "nested", "y"): {PersistenceAttribute.READONLY},
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
        attribute_props=attribute_props,
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

    attribute_props = compute_attribute_persistence(prios, data_eval, data_disk)

    assert attribute_props == {
        ("foo",): {PersistenceAttribute.READONLY},
        ("foo", "bar"): {PersistenceAttribute.READONLY},
    }

    update = {
        "foo": {
            "bar": "new value",  # <- user sets this value
        },
    }
    with pytest.raises(ClanError) as error:
        calc_patches(
            data_disk, update, all_values=data_eval, attribute_props=attribute_props
        )

    assert "Path 'foo.bar' is readonly." in str(error.value)


def test_calculate_static_data_no_static_sets() -> None:
    all_values: dict = {
        "instance": {
            "hello": {
                "static": {},
            }
        }
    }
    persisted: dict = {"instance": {"hello": {}}}
    attribute_props = {
        ("instance",): {PersistenceAttribute.WRITE},
        ("instance", "hello"): {
            PersistenceAttribute.WRITE,
            PersistenceAttribute.DELETE,
        },
        ("instance", "hello", "static"): {PersistenceAttribute.WRITE},
    }

    update: dict = {
        "instance": {
            # static is a key that is defined in nix, and cannot be deleted
            # It needs to be present.
            "hello": {}  # Error: "static" cannot be deleted
        }
    }

    with pytest.raises(ClanError) as error:
        calc_patches(
            persisted=persisted,
            all_values=all_values,
            update=update,
            attribute_props=attribute_props,
        )

    assert "Cannot delete path 'instance.hello.static'" in str(error.value)


# Same as above, but using legacy priorities
# This allows deletion, but is slightly wrong.
# The correct behavior requires nixos >= 25.11
def test_calculate_static_data_no_static_sets_legacy() -> None:
    prios = {
        "instance": {
            "__prio": 100,  # <- writeable: "foo"
            "hello": {
                "__prio": 100,
                "static": {"__prio": 100},
            },
        },
    }

    all_values: dict = {
        "instance": {
            "hello": {
                "static": {},
            }
        }
    }
    persisted: dict = {"instance": {"hello": {}}}

    attribute_props = compute_attribute_persistence(prios, all_values, persisted)

    update: dict = {
        "instance": {
            "hello": {},  # <- user removes "static"
        },
    }

    updates, deletes = calc_patches(
        persisted, update, all_values=all_values, attribute_props=attribute_props
    )
    assert updates == {("instance", "hello"): {}}
    assert deletes == {("instance", "hello", "static")}


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

    attribute_props = compute_attribute_persistence(prios, data_eval, data_disk)

    assert attribute_props == {
        ("foo",): {PersistenceAttribute.WRITE},
    }

    # Add "C" to the list
    update = {"foo": ["A", "B", "C"]}  # User wants to add "C"

    patchset, _ = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        attribute_props=attribute_props,
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
        attribute_props=attribute_props,
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

    attribute_props = compute_attribute_persistence(prios, data_eval, data_disk)

    assert attribute_props == {
        ("foo",): {PersistenceAttribute.WRITE},
    }

    # Add "A" to the list
    update = {"foo": ["A", "B", "A"]}  # User wants to add duplicate "A"

    with pytest.raises(ClanError) as error:
        calc_patches(
            data_disk, update, all_values=data_eval, attribute_props=attribute_props
        )

    assert "Path 'foo' contains list duplicates: ['A']" in str(error.value)


def test_dont_persist_defaults() -> None:
    """Default values should not be persisted to disk if not explicitly requested by the user."""
    introspection = {
        "enabled": {"__prio": 1500},
        "config": {
            "__prio": 100,
            "foo": {  # <- default in the 'config' submodule
                "__prio": 1500,
            },
        },
    }
    data_eval = {
        "enabled": True,
        "config": {"foo": "bar"},
    }
    data_disk: dict[str, Any] = {}
    attribute_props = compute_attribute_persistence(introspection, data_eval, data_disk)

    assert attribute_props == {
        ("enabled",): {PersistenceAttribute.WRITE},
        ("config",): {PersistenceAttribute.WRITE},
        ("config", "foo"): {PersistenceAttribute.WRITE, PersistenceAttribute.DELETE},
    }

    update = deepcopy(data_eval)
    set_value_by_path(update, "config.foo", "foo")

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        attribute_props=attribute_props,
    )
    assert patchset == {("config", "foo"): "foo"}
    assert delete_set == set()


def test_set_null() -> None:
    data_eval: dict = {
        "root": {
            "foo": {},
            "bar": {},
        }
    }
    data_disk = data_eval

    # User set Foo to null
    # User deleted bar
    update = {"root": {"foo": None}}

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        attribute_props=compute_attribute_persistence(
            {"root": {"__prio": 100, "foo": {"__prio": 100}, "bar": {"__prio": 100}}},
            data_eval,
            data_disk,
        ),
    )
    assert patchset == {("root", "foo"): None}
    assert delete_set == {("root", "bar")}


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

    attribute_props = compute_attribute_persistence(prios, data_eval, data_disk)
    assert attribute_props == {
        ("machines",): {PersistenceAttribute.WRITE},
        ("machines", "foo"): {PersistenceAttribute.WRITE, PersistenceAttribute.DELETE},
        ("machines", "foo", "name"): {
            PersistenceAttribute.WRITE,
            PersistenceAttribute.DELETE,
        },
        ("machines", "bar"): {PersistenceAttribute.WRITE, PersistenceAttribute.DELETE},
        ("machines", "bar", "name"): {
            PersistenceAttribute.WRITE,
            PersistenceAttribute.DELETE,
        },
        ("machines", "naz"): {PersistenceAttribute.WRITE, PersistenceAttribute.DELETE},
        ("machines", "naz", "name"): {
            PersistenceAttribute.WRITE,
            PersistenceAttribute.DELETE,
        },
    }

    # Delete machine "bar"  from the inventory
    update = deepcopy(data_eval)
    delete_by_path(update, "machines.bar")

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        attribute_props=attribute_props,
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

    attribute_props = compute_attribute_persistence(prios, data_eval, data_disk)

    assert attribute_props == {
        ("foo",): {PersistenceAttribute.WRITE},
    }

    # set foo to an int but it is a list
    update: dict = {"foo": 1}

    with pytest.raises(ClanError) as error:
        calc_patches(
            data_disk, update, all_values=data_eval, attribute_props=attribute_props
        )

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

    attribute_props = compute_attribute_persistence(prios, data_eval, data_disk)

    assert attribute_props == {
        ("foo",): {PersistenceAttribute.WRITE},
        ("foo", "bar"): {PersistenceAttribute.WRITE, PersistenceAttribute.DELETE},
    }

    # remove all keys from foo
    update: dict = {"foo": {}}

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        attribute_props=attribute_props,
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

    attribute_props = compute_attribute_persistence(prios, data_eval, data_disk)

    assert attribute_props == {
        ("foo",): {PersistenceAttribute.WRITE},
        ("foo", "bar"): {PersistenceAttribute.WRITE, PersistenceAttribute.DELETE},
        ("foo", "bar", "name"): {
            PersistenceAttribute.WRITE,
            PersistenceAttribute.DELETE,
        },
        ("foo", "bar", "info"): {
            PersistenceAttribute.WRITE,
            PersistenceAttribute.DELETE,
        },
        ("foo", "bar", "other"): {
            PersistenceAttribute.WRITE,
            PersistenceAttribute.DELETE,
        },
        ("foo", "other"): {PersistenceAttribute.WRITE, PersistenceAttribute.DELETE},
        ("foo", "other", "name"): {
            PersistenceAttribute.WRITE,
            PersistenceAttribute.DELETE,
        },
        ("foo", "other", "info"): {
            PersistenceAttribute.WRITE,
            PersistenceAttribute.DELETE,
        },
        ("foo", "other", "other"): {
            PersistenceAttribute.WRITE,
            PersistenceAttribute.DELETE,
        },
    }
    # remove all keys from foo

    patchset, delete_set = calc_patches(
        data_disk,
        update,
        all_values=data_eval,
        attribute_props=attribute_props,
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

    attribute_props = compute_attribute_persistence(prios, data_eval, data_disk)

    # TOOD: Collapse these paths, by early stopping the recursion in
    # compute_attribute_persistence
    assert attribute_props == {
        ("foo",): {PersistenceAttribute.READONLY},
        ("foo", "bar"): {PersistenceAttribute.READONLY},
        ("foo", "bar", "name"): {PersistenceAttribute.READONLY},
        ("foo", "bar", "info"): {PersistenceAttribute.READONLY},
        ("foo", "bar", "other"): {PersistenceAttribute.READONLY},
    }

    # remove all keys from foo
    with pytest.raises(ClanError) as error:
        calc_patches(
            data_disk, update, all_values=data_eval, attribute_props=attribute_props
        )

    assert "Cannot delete path 'foo.bar'" in str(error.value)


# --- test merge_objects ---


def test_merge_objects_empty() -> None:
    obj1: dict[str, int] = {}  # type: ignore[var-annotated]
    obj2: dict[str, int] = {}  # type: ignore[var-annotated]

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
