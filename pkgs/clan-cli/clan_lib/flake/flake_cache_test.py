import subprocess
from pathlib import Path
from sys import platform
from unittest.mock import patch

import pytest
from clan_cli.tests.fixtures_flakes import ClanFlake

from clan_lib.flake.flake import (
    Flake,
    FlakeCache,
    FlakeCacheEntry,
    Selector,
    find_store_references,
    get_physical_store_path,
    is_pure_store_path,
    parse_selector,
)


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
        "nixosConfigurations.*.config.networking.hostName",
    )
    flake1.select("nixosConfigurations.*.config.networking.hostName")
    flake1.select("nixosConfigurations.*.config.networking.{hostName,hostId}")
    flake2.invalidate_cache()
    assert flake2._cache.is_cached(  # noqa: SLF001
        "nixosConfigurations.*.config.networking.{hostName,hostId}",
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
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that is_cached correctly handles CLAN_TEST_STORE paths.

    This is a regression test for the bug where cached store paths are not
    checked for existence when CLAN_TEST_STORE is set, because the cache
    only checks existence for paths starting with NIX_STORE_DIR (/nix/store).
    """
    # Create a temporary store that mirrors the /nix/store structure
    test_store = tmp_path / "test-store"
    nix_store = test_store / "nix" / "store"
    nix_store.mkdir(parents=True)

    # Set CLAN_TEST_STORE environment variable
    monkeypatch.setenv("CLAN_TEST_STORE", str(test_store))
    # Ensure NIX_STORE_DIR is not set (typical scenario)
    monkeypatch.delenv("NIX_STORE_DIR", raising=False)

    # Create a fake store path that follows the real /nix/store pattern
    # This is what Nix would actually return even in a chroot
    fake_store_hash = "abc123def456ghi789jkl012mno345pqr"
    fake_store_name = f"{fake_store_hash}-test-output"
    fake_store_path = nix_store / fake_store_name
    fake_store_path.write_text("test content")

    # Create a cache entry
    cache = FlakeCacheEntry()

    # Insert a store path into the cache (as Nix would return it)
    nix_store_path = f"/nix/store/{fake_store_name}"
    selectors = parse_selector("testOutput")
    cache.insert(nix_store_path, selectors)

    # Verify the path is cached and exists
    assert cache.is_cached(selectors), "Path should be cached"
    # The physical path should exist in the test store
    assert get_physical_store_path(nix_store_path).exists(), (
        "Physical path should exist"
    )

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
        my_flake,
        "get_from_nix",
        wraps=my_flake.get_from_nix,
    ) as tracked_build:
        assert tracked_build.call_count == 0
        my_flake.select("clanInternals.inventoryClass.inventory.meta")
        assert tracked_build.call_count == 1
        my_flake.select("clanInternals.inventoryClass.inventory.meta")
        assert tracked_build.call_count == 1


def test_cache_is_cached_with_nix_store_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
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
    monkeypatch.delenv("CLAN_TEST_STORE", raising=False)
    monkeypatch.delenv("NIX_REMOTE", raising=False)
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


def test_store_path_with_line_numbers_not_wrapped() -> None:
    """Test that store paths with line numbers are not wrapped in outPath dict.

    This is a regression test for the bug where strings like:
    /nix/store/abc-file.nix:123
    were being treated as store paths and wrapped in {"outPath": ...} dict,
    when they should be stored as plain strings.
    """
    cache = FlakeCacheEntry()

    # Test that a path with line number is NOT wrapped in outPath
    # Use a realistic store path hash (32 chars in base32)
    path_with_line = "/nix/store/abc123def456ghi789jkl012mno345pqr-file.nix:42"
    selectors: list[Selector] = []
    cache.insert(path_with_line, selectors)

    # Should be stored as a plain string, not wrapped
    assert cache.value == path_with_line
    assert not isinstance(cache.value, dict)

    # Test that a regular store path IS wrapped in outPath
    cache2 = FlakeCacheEntry()
    regular_store_path = "/nix/store/abc123def456ghi789jkl012mno345pqr-package"
    cache2.insert(regular_store_path, [])

    # Should be wrapped in outPath dict
    assert isinstance(cache2.value, dict)
    assert "outPath" in cache2.value
    assert cache2.value["outPath"].value == regular_store_path

    # Test path with multiple colons (line:column format)
    cache3 = FlakeCacheEntry()
    path_with_line_col = "/nix/store/xyz789abc123def456ghi789jkl012mno-source.nix:10:5"
    cache3.insert(path_with_line_col, [])

    # Should be stored as plain string
    assert cache3.value == path_with_line_col
    assert not isinstance(cache3.value, dict)


def test_store_reference_helpers() -> None:
    """Test the store reference helper functions."""
    # Test find_store_references
    assert find_store_references("/nix/store/abc123-pkg") == ["/nix/store/abc123-pkg"]
    assert find_store_references("/nix/store/abc123-file.nix:42") == [
        "/nix/store/abc123-file.nix",
    ]
    assert find_store_references("/nix/store/abc123-src/lib/file.nix:42:10") == [
        "/nix/store/abc123-src",
    ]

    # Multiple references
    multi_ref = "error at /nix/store/abc123-src/file.nix:42 and /nix/store/xyz789-lib/lib.nix:10"
    refs = find_store_references(multi_ref)
    assert len(refs) == 2
    assert "/nix/store/abc123-src" in refs
    assert "/nix/store/xyz789-lib" in refs

    # No references
    assert find_store_references("/home/user/file.nix") == []
    assert find_store_references("no store paths here") == []

    # Test is_pure_store_path
    assert is_pure_store_path("/nix/store/abc123def456ghi789jkl012mno345pqr-package")
    assert is_pure_store_path("/nix/store/abc123def456ghi789jkl012mno345pqr-source")
    assert not is_pure_store_path(
        "/nix/store/abc123def456ghi789jkl012mno345pqr-file.nix:42",
    )
    assert not is_pure_store_path(
        "/nix/store/abc123def456ghi789jkl012mno345pqr-src/subdir/file.nix",
    )
    assert not is_pure_store_path("/home/user/file")


def test_cache_with_multiple_store_references() -> None:
    """Test caching behavior with strings containing multiple store references."""
    cache = FlakeCacheEntry()

    # String with multiple store references (none exist)
    multi_ref = "Error at /nix/store/nonexistent1-src/file.nix:42 and /nix/store/nonexistent2-lib/lib.nix:10"
    cache.insert(multi_ref, [])

    assert cache.value == multi_ref
    assert isinstance(cache.value, str)

    # Should return False since none of the referenced paths exist
    assert not cache.is_cached([])


def test_store_references_with_custom_store_dir(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test store reference detection with custom NIX_STORE_DIR."""
    # Set custom store directory
    monkeypatch.setenv("NIX_STORE_DIR", "/custom/store")

    # Test find_store_references with custom dir
    assert find_store_references("/custom/store/abc123-pkg") == [
        "/custom/store/abc123-pkg",
    ]
    assert find_store_references("/custom/store/abc123-file.nix") == [
        "/custom/store/abc123-file.nix",
    ]

    # Test is_pure_store_path with custom dir
    assert is_pure_store_path("/custom/store/abc123def456ghi789jkl012mno345pqr-package")
    assert not is_pure_store_path(
        "/custom/store/abc123def456ghi789jkl012mno345pqr-file.nix:42",
    )
    assert not is_pure_store_path(
        "/nix/store/abc123def456ghi789jkl012mno345pqr-package",
    )


def test_cache_path_with_line_numbers(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test that is_cached correctly handles store paths with line numbers appended.

    This is a regression test for the bug where cached store paths with line numbers
    (e.g., /nix/store/path:123) are not properly checked for existence.
    """
    # Create a temporary store that mirrors the /nix/store structure
    test_store = tmp_path / "test-store"
    nix_store = test_store / "nix" / "store"
    nix_store.mkdir(parents=True)

    # Set CLAN_TEST_STORE environment variable
    monkeypatch.setenv("CLAN_TEST_STORE", str(test_store))

    # Create a fake store path that follows the real /nix/store pattern
    fake_store_hash = "abc123def456ghi789jkl012mno345pqr"
    fake_store_name = f"{fake_store_hash}-source-file.nix"
    fake_store_path = nix_store / fake_store_name
    fake_store_path.write_text("# nix source file\n{ foo = 123; }")

    # Create cache entries for paths with line numbers
    cache = FlakeCacheEntry()

    # Test single line number format (as Nix would return it)
    nix_path_with_line = f"/nix/store/{fake_store_name}:42"
    selectors = parse_selector("testPath1")
    cache.insert(nix_path_with_line, selectors)

    # Test line:column format
    nix_path_with_line_col = f"/nix/store/{fake_store_name}:42:10"
    selectors2 = parse_selector("testPath2")
    cache.insert(nix_path_with_line_col, selectors2)

    # Test path with colon but non-numeric suffix (should not be treated as line number)
    # This would be a regular file path, not in the store
    path_with_colon = tmp_path / "file:with:colons"
    path_with_colon.write_text("test")
    selectors3 = parse_selector("testPath3")
    cache.insert(str(path_with_colon), selectors3)

    # Before the fix: These would return True even though the exact paths don't exist
    # After the fix: They check the base file path exists
    assert cache.is_cached(parse_selector("testPath1")), (
        "Path with line number should be cached when base file exists"
    )
    assert cache.is_cached(parse_selector("testPath2")), (
        "Path with line:column should be cached when base file exists"
    )
    assert cache.is_cached(parse_selector("testPath3")), (
        "Path with colons in filename should be cached when file exists"
    )

    # Now delete the base file
    fake_store_path.unlink()

    # After deletion, paths with line numbers should not be cached
    assert not cache.is_cached(parse_selector("testPath1")), (
        "Path with line number should not be cached when base file doesn't exist"
    )
    assert not cache.is_cached(parse_selector("testPath2")), (
        "Path with line:column should not be cached when base file doesn't exist"
    )

    # Path with colons in name still exists
    assert cache.is_cached(parse_selector("testPath3")), (
        "Path with colons in filename should still be cached"
    )

    # Test with regular /nix/store paths
    monkeypatch.delenv("CLAN_TEST_STORE", raising=False)
    cache2 = FlakeCacheEntry()
    nix_path_with_line = "/nix/store/0123456789abcdefghijklmnopqrstuv-source.nix:123"
    cache2.insert({"nixPath": nix_path_with_line}, [])

    # The path is stored under the nixPath key, and since it starts with /nix/store
    # and has a line number, _check_path_exists will strip the line number and check
    # if the base file exists. Since it doesn't exist, this should return False.
    assert not cache2.is_cached(parse_selector("nixPath")), (
        "Nix store path with line number should not be cached when file doesn't exist"
    )


def test_reinserting_store_path_value() -> None:
    """Test that reinserting the same store path value doesn't cause conflicts.

    This is a regression test for the bug where a store path was first inserted
    as a pure path (wrapped in outPath), and then the same value was inserted
    again as a plain string, causing a TypeError.
    """
    cache = FlakeCacheEntry()

    # First insert as pure store path - gets wrapped in outPath
    pure_path = "/nix/store/abc123def456ghi789jkl012mno345pqr-source"
    cache.insert(pure_path, [])

    assert isinstance(cache.value, dict)
    assert "outPath" in cache.value
    assert cache.value["outPath"].value == pure_path

    # Now try to insert the same value again - should not raise
    cache.insert(pure_path, [])

    # Value should remain unchanged
    assert isinstance(cache.value, dict)
    assert "outPath" in cache.value
    assert cache.value["outPath"].value == pure_path
