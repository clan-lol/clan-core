import contextlib
import logging
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest
from clan_cli.tests.fixtures_flakes import ClanFlake

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


def test_insert_and_iscached() -> None:
    test_cache = FlakeCacheEntry()
    selectors = parse_selector("x.y.z")
    test_cache.insert("x", selectors)
    assert test_cache["x"]["y"]["z"].value == "x"
    assert test_cache.is_cached(selectors)
    assert not test_cache.is_cached(parse_selector("x.y"))
    assert test_cache.is_cached(parse_selector("x.y.z.1"))
    assert not test_cache.is_cached(parse_selector("x.*.z"))
    assert test_cache.is_cached(parse_selector("x.{y}.z"))
    assert test_cache.is_cached(parse_selector("x.?y.z"))
    assert not test_cache.is_cached(parse_selector("x.?z.z"))

    test_cache = FlakeCacheEntry()
    selectors = parse_selector("x.*.z")
    test_cache.insert({"y": "x"}, selectors)
    assert test_cache["x"]["y"]["z"].value == "x"
    assert test_cache.is_cached(selectors)
    assert not test_cache.is_cached(parse_selector("x.y"))
    assert not test_cache.is_cached(parse_selector("x.y.x"))
    assert test_cache.is_cached(parse_selector("x.y.z.1"))
    assert test_cache.is_cached(parse_selector("x.{y}.z"))
    assert test_cache.is_cached(parse_selector("x.{y,z}.z"))
    assert test_cache.is_cached(parse_selector("x.{y,?z}.z"))
    assert test_cache.is_cached(parse_selector("x.?y.z"))
    assert test_cache.is_cached(parse_selector("x.?z.z"))

    test_cache = FlakeCacheEntry()
    selectors = parse_selector("x.{y}.z")
    test_cache.insert({"y": "x"}, selectors)
    assert test_cache["x"]["y"]["z"].value == "x"
    assert test_cache.is_cached(selectors)
    assert not test_cache.is_cached(parse_selector("x.y"))
    assert test_cache.is_cached(parse_selector("x.y.z.1"))
    assert not test_cache.is_cached(parse_selector("x.*.z"))
    assert test_cache.is_cached(parse_selector("x.{y}.z"))
    assert test_cache.is_cached(parse_selector("x.?y.z"))
    assert not test_cache.is_cached(parse_selector("x.?z.z"))

    test_cache = FlakeCacheEntry()
    selectors = parse_selector("x.?y.z")
    test_cache.insert({"y": "x"}, selectors)
    assert test_cache["x"]["y"]["z"].value == "x"
    assert test_cache.is_cached(selectors)
    assert not test_cache.is_cached(parse_selector("x.y"))
    assert test_cache.is_cached(parse_selector("x.y.z.1"))
    assert not test_cache.is_cached(parse_selector("x.*.z"))
    assert test_cache.is_cached(parse_selector("x.{y}.z"))
    assert test_cache.is_cached(parse_selector("x.?y.z"))
    assert not test_cache.is_cached(parse_selector("x.?z.z"))

    test_cache = FlakeCacheEntry()
    selectors = parse_selector("x.?y.z")
    test_cache.insert({}, selectors)
    assert test_cache["x"]["y"].exists is False
    assert test_cache.is_cached(selectors)
    assert test_cache.is_cached(parse_selector("x.y"))
    assert test_cache.is_cached(parse_selector("x.y.z.1"))
    assert test_cache.is_cached(parse_selector("x.?y.z.1"))
    assert not test_cache.is_cached(parse_selector("x.*.z"))
    assert test_cache.is_cached(parse_selector("x.{y}.z"))
    assert test_cache.is_cached(parse_selector("x.?y.abc"))
    assert not test_cache.is_cached(parse_selector("x.?z.z"))

    test_cache = FlakeCacheEntry()
    selectors = parse_selector("x.{y,z}.z")
    test_cache.insert({"y": 1, "z": 2}, selectors)
    assert test_cache["x"]["y"]["z"].value == 1
    assert test_cache["x"]["z"]["z"].value == 2
    assert test_cache.is_cached(selectors)
    assert not test_cache.is_cached(parse_selector("x.y"))
    assert test_cache.is_cached(parse_selector("x.y.z.1"))
    assert not test_cache.is_cached(parse_selector("x.*.z"))
    assert test_cache.is_cached(parse_selector("x.{y}.z"))
    assert not test_cache.is_cached(parse_selector("x.?y.abc"))
    assert test_cache.is_cached(parse_selector("x.?z.z"))

    test_cache = FlakeCacheEntry()
    selectors = parse_selector("x.y")
    test_cache.insert(1, selectors)
    selectors = parse_selector("x.z")
    test_cache.insert(2, selectors)
    assert test_cache["x"]["y"].value == 1
    assert test_cache["x"]["z"].value == 2
    assert test_cache.is_cached(parse_selector("x.y"))
    assert test_cache.is_cached(parse_selector("x.y.z.1"))
    assert not test_cache.is_cached(parse_selector("x.*.z"))
    assert test_cache.is_cached(parse_selector("x.{y}.z"))
    assert test_cache.is_cached(parse_selector("x.?y.abc"))
    assert test_cache.is_cached(parse_selector("x.?z.z"))
    assert not test_cache.is_cached(parse_selector("x.?x.z"))

    test_cache = FlakeCacheEntry()
    selectors = parse_selector("x.y.z")
    test_cache.insert({"a": {"b": {"c": 1}}}, selectors)
    assert test_cache.is_cached(selectors)
    assert test_cache.is_cached(parse_selector("x.y.z.a.b.c"))
    assert test_cache.is_cached(parse_selector("x.y.z.a.b"))
    assert test_cache.is_cached(parse_selector("x.y.z.a"))
    assert test_cache.is_cached(parse_selector("x.y.z"))
    assert not test_cache.is_cached(parse_selector("x.y"))
    assert not test_cache.is_cached(parse_selector("x"))
    assert test_cache.is_cached(parse_selector("x.y.z.xxx"))

    test_cache = FlakeCacheEntry()
    selectors = parse_selector("x.y")
    test_cache.insert(1, selectors)
    with pytest.raises(TypeError):
        test_cache.insert(2, selectors)
    assert test_cache["x"]["y"].value == 1


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


def test_out_path() -> None:
    testdict = {"x": {"y": [123, 345, 456], "z": "/nix/store/bla"}}
    test_cache = FlakeCacheEntry()
    test_cache.insert(testdict, [])
    selectors = parse_selector("x.z")
    assert test_cache.select(selectors) == "/nix/store/bla"
    selectors = parse_selector("x.z.outPath")
    assert test_cache.select(selectors) == "/nix/store/bla"


@pytest.mark.with_core
def test_flake_caching(flake: ClanFlake) -> None:
    m1 = flake.machines["machine1"]
    m1["nixpkgs"]["hostPlatform"] = "x86_64-linux"
    flake.machines["machine2"] = m1.copy()
    flake.machines["machine3"] = m1.copy()
    flake.refresh()

    flake_ = Flake(str(flake.path))
    hostnames = flake_.select("nixosConfigurations.*.config.networking.hostName")
    assert hostnames == {
        "machine1": "machine1",
        "machine2": "machine2",
        "machine3": "machine3",
    }


@pytest.mark.with_core
def test_cache_persistance(flake: ClanFlake) -> None:
    m1 = flake.machines["machine1"]
    m1["nixpkgs"]["hostPlatform"] = "x86_64-linux"
    flake.refresh()

    flake1 = Flake(str(flake.path))
    flake2 = Flake(str(flake.path))
    flake1.invalidate_cache()
    flake2.invalidate_cache()
    assert isinstance(flake1._cache, FlakeCache)  # noqa: SLF001
    assert isinstance(flake2._cache, FlakeCache)  # noqa: SLF001
    assert not flake1._cache.is_cached(  # noqa: SLF001
        "nixosConfigurations.*.config.networking.hostName"
    )
    flake1.select("nixosConfigurations.*.config.networking.hostName")
    flake1.select("nixosConfigurations.*.config.networking.{hostName,hostId}")
    flake2.invalidate_cache()
    assert flake2._cache.is_cached(  # noqa: SLF001
        "nixosConfigurations.*.config.networking.{hostName,hostId}"
    )


@pytest.mark.with_core
def test_conditional_all_selector(flake: ClanFlake) -> None:
    m1 = flake.machines["machine1"]
    m1["nixpkgs"]["hostPlatform"] = "x86_64-linux"
    flake.refresh()

    flake1 = Flake(str(flake.path))
    flake2 = Flake(str(flake.path))
    flake1.invalidate_cache()
    flake2.invalidate_cache()
    assert isinstance(flake1._cache, FlakeCache)  # noqa: SLF001
    assert isinstance(flake2._cache, FlakeCache)  # noqa: SLF001
    log.info("First select")
    res1 = flake1.select("inputs.*.{?clan,?missing}.templates.*.*.description")

    log.info("Second (cached) select")
    res2 = flake1.select("inputs.*.{?clan,?missing}.templates.*.*.description")

    assert res1 == res2
    assert res1["clan-core"].get("clan") is not None

    flake2.invalidate_cache()


# Test that the caching works
@pytest.mark.with_core
def test_caching_works(flake: ClanFlake) -> None:
    my_flake = Flake(str(flake.path))

    with patch.object(
        my_flake, "get_from_nix", wraps=my_flake.get_from_nix
    ) as tracked_build:
        assert tracked_build.call_count == 0
        my_flake.select("clanInternals.inventory.meta")
        assert tracked_build.call_count == 1
        my_flake.select("clanInternals.inventory.meta")
        assert tracked_build.call_count == 1


@pytest.mark.with_core
def test_cache_gc(monkeypatch: pytest.MonkeyPatch) -> None:
    with TemporaryDirectory() as tempdir_:
        tempdir = Path(tempdir_)

        monkeypatch.setenv("NIX_STATE_DIR", str(tempdir / "var"))
        monkeypatch.setenv("NIX_LOG_DIR", str(tempdir / "var" / "log"))
        monkeypatch.setenv("NIX_STORE_DIR", str(tempdir / "store"))
        monkeypatch.setenv("NIX_CACHE_HOME", str(tempdir / "cache"))
        monkeypatch.setenv("HOME", str(tempdir / "home"))
        with contextlib.suppress(KeyError):
            monkeypatch.delenv("CLAN_TEST_STORE")
        monkeypatch.setenv("NIX_BUILD_TOP", str(tempdir / "build"))

        test_file = tempdir / "flake" / "testfile"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test")

        test_flake = tempdir / "flake" / "flake.nix"
        test_flake.write_text("""
            {
              outputs = _: {
                testfile = ./testfile;
              };
            }
        """)

        my_flake = Flake(str(tempdir / "flake"))
        my_flake.select(
            "testfile", nix_options=["--sandbox-build-dir", str(tempdir / "build")]
        )
        assert my_flake._cache is not None  # noqa: SLF001
        assert my_flake._cache.is_cached("testfile")  # noqa: SLF001
        subprocess.run(["nix-collect-garbage"], check=True)
        assert not my_flake._cache.is_cached("testfile")  # noqa: SLF001


# This test fails because the CI sandbox does not have the required packages to run the generators
# maybe @DavHau or @Qubasa can fix this at some point :)
# @pytest.mark.with_core
# def test_cache_invalidation(flake: ClanFlake, sops_setup: SopsSetup) -> None:
#     m1 = flake.machines["machine1"]
#     m1["nixpkgs"]["hostPlatform"] = "x86_64-linux"
#     flake.refresh()
#     clan_dir = Flake(str(flake.path))
#     machine1 = Machine(
#         name="machine1",
#         flake=clan_dir,
#     )
#     sops_setup.init(flake.path)
#     generate_vars([machine1])
#
#     flake.inventory["services"] = {
#         "sshd": {
#             "someid": {
#                 "roles": {
#                     "server": {
#                         "machines": ["machine1"],
#                     }
#                 }
#             }
#         }
#     }
#     flake.refresh()
#     machine1.flush_caches()  # because flake.refresh() does not invalidate the cache but it writes into the directory
#
#     generate_vars([machine1])
#     vpn_ip = (
#         get_var(str(clan_dir), machine1.name, "openssh/ssh.id_ed25519")
#         .value.decode()
#         .strip("\n")
#     )
#     assert vpn_ip is not None
