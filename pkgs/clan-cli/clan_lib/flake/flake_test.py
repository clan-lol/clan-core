import logging

import pytest
from clan_cli.tests.fixtures_flakes import ClanFlake, create_test_machine_config

from clan_lib.flake.flake import (
    Flake,
    FlakeCache,
    FlakeCacheEntry,
    parse_selector,
    selectors_as_dict,
)

log = logging.getLogger(__name__)


def test_parse_selector() -> None:
    selectors = parse_selector("x")
    assert selectors_as_dict(selectors) == [
        {"type": "str", "value": "x"},
    ]
    selectors = parse_selector("?x")
    assert selectors_as_dict(selectors) == [
        {"type": "maybe", "value": "x"},
    ]
    selectors = parse_selector('"x"')
    assert selectors_as_dict(selectors) == [
        {"type": "str", "value": "x"},
    ]
    selectors = parse_selector("*")
    assert selectors_as_dict(selectors) == [
        {"type": "all"},
    ]
    selectors = parse_selector("{x}")
    assert selectors_as_dict(selectors) == [
        {
            "type": "set",
            "value": [
                {"type": "str", "value": "x"},
            ],
        },
    ]
    selectors = parse_selector("{x}.y")
    assert selectors_as_dict(selectors) == [
        {
            "type": "set",
            "value": [
                {"type": "str", "value": "x"},
            ],
        },
        {"type": "str", "value": "y"},
    ]
    selectors = parse_selector("x.y.z")
    assert selectors_as_dict(selectors) == [
        {"type": "str", "value": "x"},
        {"type": "str", "value": "y"},
        {"type": "str", "value": "z"},
    ]
    selectors = parse_selector("x.*")
    assert selectors_as_dict(selectors) == [
        {"type": "str", "value": "x"},
        {"type": "all"},
    ]
    selectors = parse_selector("*.x")
    assert selectors_as_dict(selectors) == [
        {"type": "all"},
        {"type": "str", "value": "x"},
    ]
    selectors = parse_selector("x.*.z")
    assert selectors_as_dict(selectors) == [
        {"type": "str", "value": "x"},
        {"type": "all"},
        {"type": "str", "value": "z"},
    ]
    selectors = parse_selector("x.{y,z}")
    assert selectors_as_dict(selectors) == [
        {"type": "str", "value": "x"},
        {
            "type": "set",
            "value": [
                {"type": "str", "value": "y"},
                {"type": "str", "value": "z"},
            ],
        },
    ]
    selectors = parse_selector("x.?zzz.{y,?z,x,*}")
    assert selectors_as_dict(selectors) == [
        {"type": "str", "value": "x"},
        {"type": "maybe", "value": "zzz"},
        {
            "type": "set",
            "value": [
                {"type": "str", "value": "y"},
                {"type": "maybe", "value": "z"},
                {"type": "str", "value": "x"},
                {"type": "str", "value": "*"},
            ],
        },
    ]

    selectors = parse_selector('x."?zzz".?zzz\\.asd..{y,\\?z,"x,",*}')
    assert selectors_as_dict(selectors) == [
        {"type": "str", "value": "x"},
        {"type": "str", "value": "?zzz"},
        {"type": "maybe", "value": "zzz.asd"},
        {"type": "str", "value": ""},
        {
            "type": "set",
            "value": [
                {"type": "str", "value": "y"},
                {"type": "str", "value": "?z"},
                {"type": "str", "value": "x,"},
                {"type": "str", "value": "*"},
            ],
        },
    ]


def test_select() -> None:
    test_cache = FlakeCacheEntry()

    test_cache.insert("bla", parse_selector("a.b.c"))
    assert test_cache.select(parse_selector("a.b.c")) == "bla"
    assert test_cache.select(parse_selector("a.b")) == {"c": "bla"}
    assert test_cache.select(parse_selector("a")) == {"b": {"c": "bla"}}
    assert test_cache.select(parse_selector("a.b.?c")) == {"c": "bla"}
    assert test_cache.select(parse_selector("a.?b.?c")) == {"b": {"c": "bla"}}
    assert test_cache.select(parse_selector("a.?c")) == {}
    assert test_cache.select(parse_selector("a.?x.c")) == {}
    assert test_cache.select(parse_selector("a.*")) == {"b": {"c": "bla"}}
    assert test_cache.select(parse_selector("a.*.*")) == {"b": {"c": "bla"}}
    assert test_cache.select(parse_selector("a.*.c")) == {"b": "bla"}
    assert test_cache.select(parse_selector("a.b.*")) == {"c": "bla"}
    assert test_cache.select(parse_selector("a.{b}.c")) == {"b": "bla"}
    assert test_cache.select(parse_selector("a.{b}.{c}")) == {"b": {"c": "bla"}}
    assert test_cache.select(parse_selector("a.b.{c}")) == {"c": "bla"}
    assert test_cache.select(parse_selector("a.{?b}.c")) == {"b": "bla"}
    assert test_cache.select(parse_selector("a.{?b,?x}.c")) == {"b": "bla"}
    with pytest.raises(KeyError):
        test_cache.select(parse_selector("a.b.x"))
    with pytest.raises(KeyError):
        test_cache.select(parse_selector("a.b.c.x"))
    with pytest.raises(KeyError):
        test_cache.select(parse_selector("a.{b,x}.c"))

    testdict = {"x": {"y": [123, 345, 456], "z": "bla"}}
    test_cache.insert(testdict, parse_selector("testdict"))
    assert test_cache["testdict"]["x"]["z"].value == "bla"
    selectors = parse_selector("testdict.x.z")
    assert test_cache.select(selectors) == "bla"
    selectors = parse_selector("testdict.x.z.z")
    with pytest.raises(KeyError):
        test_cache.select(selectors)
    selectors = parse_selector("testdict.x.y.0")
    assert test_cache.select(selectors) == 123
    selectors = parse_selector("testdict.x.z.1")
    with pytest.raises(KeyError):
        test_cache.select(selectors)

    testdict2 = {"x": {"y": {"a": 1, "b": 2}, "z": None}, "n": {}}
    test_cache.insert(testdict2, parse_selector("testdict2"))
    assert test_cache.select(parse_selector("testdict2.n")) == {}
    assert test_cache.select(parse_selector("testdict2.?n")) == {"n": {}}
    assert test_cache.select(parse_selector("testdict2.x.*.?a")) == {"y": {"a": 1}}
    assert test_cache.select(parse_selector("testdict2.x.z.?a")) == {}
    assert test_cache.select(parse_selector("testdict2.x.z.{?a}")) == {}
    assert test_cache.select(parse_selector("testdict2.x.z.{}")) == {}
    with pytest.raises(KeyError):
        test_cache.select(parse_selector("testdict2.x.z.a"))
    with pytest.raises(KeyError):
        test_cache.select(parse_selector("testdict2.x.z.{a}"))
    with pytest.raises(KeyError):
        test_cache.select(parse_selector("testdict2.x.z.{a,?b}"))


def test_out_path() -> None:
    testdict = {"x": {"y": [123, 345, 456], "z": "/nix/store/abc-bla"}}
    test_cache = FlakeCacheEntry()
    test_cache.insert(testdict, [])
    selectors = parse_selector("x.z")
    assert test_cache.select(selectors) == "/nix/store/abc-bla"
    selectors = parse_selector("x.z.outPath")
    assert test_cache.select(selectors) == "/nix/store/abc-bla"


def test_out_path_in_multiselect_raises_exception() -> None:
    with pytest.raises(ValueError, match="Cannot use 'outPath' in multiselect"):
        parse_selector("{outPath}")

    with pytest.raises(ValueError, match="Cannot use 'outPath' in multiselect"):
        parse_selector("x.{y,outPath}")

    with pytest.raises(ValueError, match="Cannot use 'outPath' in multiselect"):
        parse_selector("a.b.{c,d,outPath,e}")

    with pytest.raises(ValueError, match="Cannot use 'outPath' in multiselect"):
        parse_selector("{?outPath}")


@pytest.mark.with_core
def test_conditional_all_selector(flake: ClanFlake) -> None:
    flake.machines["machine1"] = create_test_machine_config()
    flake.refresh()

    flake1 = Flake(str(flake.path))
    flake2 = Flake(str(flake.path))
    flake1.invalidate_cache()
    flake2.invalidate_cache()
    assert isinstance(flake1._cache, FlakeCache)
    assert isinstance(flake2._cache, FlakeCache)

    assert flake1.get_input_names() == ["clan-core", "nixpkgs"]
    log.info("First select")
    res1 = flake1.select("inputs.*.{?clan,?missing}.templates.*.*.description")

    log.info("Second (cached) select")
    res2 = flake1.select("inputs.*.{?clan,?missing}.templates.*.*.description")

    assert res1 == res2
    assert res1["clan-core"].get("clan") is not None

    flake2.invalidate_cache()
