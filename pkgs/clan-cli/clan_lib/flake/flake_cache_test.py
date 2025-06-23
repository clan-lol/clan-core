import contextlib
import subprocess
from pathlib import Path
from sys import platform
from unittest.mock import patch

import pytest
from clan_cli.tests.fixtures_flakes import ClanFlake

from clan_lib.flake.flake import Flake, FlakeCache, FlakeCacheEntry, parse_selector


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


def test_cache_is_cached_with_clan_test_store(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that is_cached correctly handles CLAN_TEST_STORE paths.

    This is a regression test for the bug where cached store paths are not
    checked for existence when CLAN_TEST_STORE is set, because the cache
    only checks existence for paths starting with NIX_STORE_DIR (/nix/store).
    """
    # Create a temporary store
    test_store = tmp_path / "test-store"
    test_store.mkdir()

    # Set CLAN_TEST_STORE environment variable
    monkeypatch.setenv("CLAN_TEST_STORE", str(test_store))
    # Ensure NIX_STORE_DIR is not set (typical scenario)
    monkeypatch.delenv("NIX_STORE_DIR", raising=False)

    # Create a fake store path in the test store
    fake_store_path = test_store / "abc123-test-output"
    fake_store_path.write_text("test content")

    # Create a cache entry
    cache = FlakeCacheEntry()

    # Insert a store path into the cache
    selectors = parse_selector("testOutput")
    cache.insert(str(fake_store_path), selectors)

    # Verify the path is cached and exists
    assert cache.is_cached(selectors), "Path should be cached"
    assert Path(cache.select(selectors)).exists(), "Path should exist"

    # Now delete the path to simulate garbage collection
    fake_store_path.unlink()
    assert not fake_store_path.exists(), "Path should be deleted"

    # After the fix: is_cached correctly returns False when the path doesn't exist
    # even for test store paths
    is_cached_result = cache.is_cached(selectors)
    assert not is_cached_result, "Cache correctly checks existence of test store paths"

    # For comparison, let's test with a /nix/store path
    cache2 = FlakeCacheEntry()
    nix_store_path = "/nix/store/fake-path-that-doesnt-exist"
    cache2.insert(nix_store_path, selectors)

    # This should return False because the path doesn't exist
    assert not cache2.is_cached(selectors), (
        "Cache correctly checks existence of /nix/store paths"
    )


# Test that the caching works
@pytest.mark.with_core
def test_caching_works(flake: ClanFlake) -> None:
    my_flake = Flake(str(flake.path))

    with patch.object(
        my_flake, "get_from_nix", wraps=my_flake.get_from_nix
    ) as tracked_build:
        assert tracked_build.call_count == 0
        my_flake.select("clanInternals.inventoryClass.inventory.meta")
        assert tracked_build.call_count == 1
        my_flake.select("clanInternals.inventoryClass.inventory.meta")
        assert tracked_build.call_count == 1


def test_cache_is_cached_with_nix_store_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test that is_cached works correctly when NIX_STORE_DIR is set to match CLAN_TEST_STORE."""
    # Create a temporary store
    test_store = tmp_path / "test-store"
    test_store.mkdir()

    # Set both CLAN_TEST_STORE and NIX_STORE_DIR to the same value
    monkeypatch.setenv("CLAN_TEST_STORE", str(test_store))
    monkeypatch.setenv("NIX_STORE_DIR", str(test_store))

    # Create a fake store path in the test store
    fake_store_path = test_store / "abc123-test-output"
    fake_store_path.write_text("test content")

    # Create a cache entry
    cache = FlakeCacheEntry()

    # Insert a store path into the cache
    selectors = parse_selector("testOutput")
    cache.insert(str(fake_store_path), selectors)

    # With NIX_STORE_DIR set correctly, is_cached should return True
    assert cache.is_cached(selectors), (
        "Cache should recognize test store path when NIX_STORE_DIR is set"
    )


@pytest.mark.with_core
def test_cache_gc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that garbage collection properly invalidates cached store paths."""
    monkeypatch.setenv("NIX_STATE_DIR", str(tmp_path / "var"))
    monkeypatch.setenv("NIX_LOG_DIR", str(tmp_path / "var" / "log"))
    monkeypatch.setenv("NIX_STORE_DIR", str(tmp_path / "store"))
    monkeypatch.setenv("NIX_CACHE_HOME", str(tmp_path / "cache"))
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    with contextlib.suppress(KeyError):
        monkeypatch.delenv("CLAN_TEST_STORE")
    monkeypatch.setenv("NIX_BUILD_TOP", str(tmp_path / "build"))

    test_file = tmp_path / "flake" / "testfile"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("test")

    test_flake = tmp_path / "flake" / "flake.nix"
    test_flake.write_text("""
        {
          outputs = _: {
            testfile = ./testfile;
          };
        }
    """)

    my_flake = Flake(
        str(tmp_path / "flake"),
        nix_options=["--sandbox-build-dir", str(tmp_path / "build")],
    )
    if platform == "darwin":
        my_flake.select("testfile")
    else:
        my_flake.select("testfile")
    assert my_flake._cache is not None  # noqa: SLF001
    assert my_flake._cache.is_cached("testfile")  # noqa: SLF001
    subprocess.run(["nix-collect-garbage"], check=True)
    assert not my_flake._cache.is_cached("testfile")  # noqa: SLF001
