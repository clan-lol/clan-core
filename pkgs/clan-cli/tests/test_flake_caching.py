import logging

import pytest
from clan_cli.flake import Flake, FlakeCache, FlakeCacheEntry
from fixtures_flakes import ClanFlake

log = logging.getLogger(__name__)


def test_select() -> None:
    testdict = {"x": {"y": [123, 345, 456], "z": "bla"}}
    test_cache = FlakeCacheEntry(testdict, [])
    assert test_cache["x"]["z"].value == "bla"
    assert test_cache.is_cached(["x", "z"])
    assert not test_cache.is_cached(["x", "y", "z"])
    assert test_cache.select(["x", "y", 0]) == 123
    assert not test_cache.is_cached(["x", "z", 1])


def test_out_path() -> None:
    testdict = {"x": {"y": [123, 345, 456], "z": "/nix/store/bla"}}
    test_cache = FlakeCacheEntry(testdict, [])
    assert test_cache.select(["x", "z"]) == "/nix/store/bla"
    assert test_cache.select(["x", "z", "outPath"]) == "/nix/store/bla"


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
    flake1.prefetch()
    flake2.prefetch()
    assert isinstance(flake1._cache, FlakeCache)  # noqa: SLF001
    assert isinstance(flake2._cache, FlakeCache)  # noqa: SLF001
    assert not flake1._cache.is_cached(  # noqa: SLF001
        "nixosConfigurations.*.config.networking.hostName"
    )
    flake1.select("nixosConfigurations.*.config.networking.hostName")
    flake1.select("nixosConfigurations.*.config.networking.{hostName,hostId}")
    flake2.prefetch()
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
    flake1.prefetch()
    flake2.prefetch()
    assert isinstance(flake1._cache, FlakeCache)  # noqa: SLF001
    assert isinstance(flake2._cache, FlakeCache)  # noqa: SLF001
    log.info("First select")
    res1 = flake1.select("inputs.*.{clan,missing}")

    log.info("Second (cached) select")
    res2 = flake1.select("inputs.*.{clan,missing}")

    assert res1 == res2
    assert res1["clan-core"].get("clan") is not None

    flake2.prefetch()
