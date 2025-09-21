from clan_lib.persist.writability import determine_writeability


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
