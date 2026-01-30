"""Tests for nix shell cache cleanup functionality."""

import os
import tempfile
import time
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import pytest

import clan_lib.nix.cache_cleanup as cache_module
from clan_lib.nix.cache_cleanup import (
    CACHE_MAX_AGE_SECONDS,
    CLEANUP_CHECK_INTERVAL,
    _cleanup_old_cache_dirs,
    maybe_cleanup_cache,
)


@pytest.fixture
def clean_cache_dir() -> Iterator[Path]:
    """Provide a clean temporary cache directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_base = Path(tmpdir) / "nix_shell_cache"
        cache_base.mkdir(parents=True)
        yield cache_base


@pytest.fixture
def reset_cleanup_state() -> Iterator[None]:
    """Reset the cleanup check timestamp before each test."""
    cache_module._last_cleanup_check = 0.0
    yield
    cache_module._last_cleanup_check = 0.0


def test_cleanup_removes_old_directories(clean_cache_dir: Path) -> None:
    """Test that directories older than CACHE_MAX_AGE are removed."""
    # Create an "old" cache directory
    old_dir = clean_cache_dir / "old_hash_1234"
    old_dir.mkdir()

    # Set mtime to be older than max age
    old_time = time.time() - CACHE_MAX_AGE_SECONDS - 3600  # 1 hour past expiry
    os.utime(old_dir, (old_time, old_time))

    with patch(
        "clan_lib.nix.cache_cleanup.clan_tmp_dir", return_value=clean_cache_dir.parent
    ):
        _cleanup_old_cache_dirs()

    assert not old_dir.exists(), "Old directory should be removed"


def test_cleanup_preserves_recent_directories(clean_cache_dir: Path) -> None:
    """Test that recently used directories are preserved."""
    # Create a "recent" cache directory
    recent_dir = clean_cache_dir / "recent_hash_5678"
    recent_dir.mkdir()

    # mtime is already "now" since we just created it

    with patch(
        "clan_lib.nix.cache_cleanup.clan_tmp_dir", return_value=clean_cache_dir.parent
    ):
        _cleanup_old_cache_dirs()

    assert recent_dir.exists(), "Recent directory should be preserved"


def test_cleanup_skips_hidden_files(clean_cache_dir: Path) -> None:
    """Test that hidden files (like .cleanup.lock) are not removed."""
    # Create hidden file
    hidden_file = clean_cache_dir / ".cleanup.lock"
    hidden_file.touch()

    # Set old mtime
    old_time = time.time() - CACHE_MAX_AGE_SECONDS - 3600
    os.utime(hidden_file, (old_time, old_time))

    with patch(
        "clan_lib.nix.cache_cleanup.clan_tmp_dir", return_value=clean_cache_dir.parent
    ):
        _cleanup_old_cache_dirs()

    assert hidden_file.exists(), "Hidden files should be preserved"


def test_cleanup_skips_non_directories(clean_cache_dir: Path) -> None:
    """Test that regular files in the cache base are not removed."""
    # Create a regular file (not a directory)
    regular_file = clean_cache_dir / "some_file"
    regular_file.touch()

    # Set old mtime
    old_time = time.time() - CACHE_MAX_AGE_SECONDS - 3600
    os.utime(regular_file, (old_time, old_time))

    with patch(
        "clan_lib.nix.cache_cleanup.clan_tmp_dir", return_value=clean_cache_dir.parent
    ):
        _cleanup_old_cache_dirs()

    assert regular_file.exists(), "Regular files should be preserved"


def test_cleanup_handles_mixed_old_and_new(clean_cache_dir: Path) -> None:
    """Test cleanup with a mix of old and new directories."""
    # Create old directory
    old_dir = clean_cache_dir / "old_hash"
    old_dir.mkdir()
    old_time = time.time() - CACHE_MAX_AGE_SECONDS - 3600
    os.utime(old_dir, (old_time, old_time))

    # Create new directory
    new_dir = clean_cache_dir / "new_hash"
    new_dir.mkdir()
    # mtime is already "now"

    with patch(
        "clan_lib.nix.cache_cleanup.clan_tmp_dir", return_value=clean_cache_dir.parent
    ):
        _cleanup_old_cache_dirs()

    assert not old_dir.exists(), "Old directory should be removed"
    assert new_dir.exists(), "New directory should be preserved"


def test_cleanup_creates_lock_file(clean_cache_dir: Path) -> None:
    """Test that cleanup creates the lock file if it doesn't exist."""
    lock_file = clean_cache_dir / ".cleanup.lock"
    assert not lock_file.exists()

    with patch(
        "clan_lib.nix.cache_cleanup.clan_tmp_dir", return_value=clean_cache_dir.parent
    ):
        _cleanup_old_cache_dirs()

    assert lock_file.exists(), "Lock file should be created"


def test_cleanup_noop_when_cache_doesnt_exist() -> None:
    """Test that cleanup is a no-op when the cache directory doesn't exist."""
    with (
        tempfile.TemporaryDirectory() as tmpdir,
        patch("clan_lib.nix.cache_cleanup.clan_tmp_dir", return_value=tmpdir),
    ):
        # Don't create the nix_shell_cache subdirectory
        # Should not raise any errors
        _cleanup_old_cache_dirs()


def test_maybe_cleanup_respects_interval(
    clean_cache_dir: Path, reset_cleanup_state: None
) -> None:
    """Test that maybe_cleanup_cache respects CLEANUP_CHECK_INTERVAL."""
    _ = reset_cleanup_state  # Used via fixture

    cleanup_call_count = [0]

    def mock_cleanup() -> None:
        cleanup_call_count[0] += 1

    with (
        patch(
            "clan_lib.nix.cache_cleanup.clan_tmp_dir",
            return_value=clean_cache_dir.parent,
        ),
        patch("clan_lib.nix.cache_cleanup._cleanup_old_cache_dirs", mock_cleanup),
    ):
        # First call should trigger cleanup
        maybe_cleanup_cache()
        assert cleanup_call_count[0] == 1, "First call should trigger cleanup"

        # Immediate second call should NOT trigger cleanup
        maybe_cleanup_cache()
        assert cleanup_call_count[0] == 1, "Second call should be throttled"

        # Simulate time passing beyond the interval
        cache_module._last_cleanup_check = time.time() - CLEANUP_CHECK_INTERVAL - 1

        # Now it should trigger again
        maybe_cleanup_cache()
        assert cleanup_call_count[0] == 2, "Call after interval should trigger cleanup"


def test_cleanup_with_zero_max_age(clean_cache_dir: Path) -> None:
    """Test cleanup with CLAN_CACHE_MAX_AGE_DAYS=0 removes all directories."""
    # Create a directory with current mtime
    cache_dir = clean_cache_dir / "some_hash"
    cache_dir.mkdir()

    # Patch the max age to 0
    with (
        patch(
            "clan_lib.nix.cache_cleanup.clan_tmp_dir",
            return_value=clean_cache_dir.parent,
        ),
        patch("clan_lib.nix.cache_cleanup.CACHE_MAX_AGE_SECONDS", 0),
    ):
        _cleanup_old_cache_dirs()

    assert not cache_dir.exists(), "Directory should be removed with max age of 0"


def test_cleanup_handles_permission_error(clean_cache_dir: Path) -> None:
    """Test that cleanup handles permission errors gracefully."""
    # Create a directory
    cache_dir = clean_cache_dir / "protected_hash"
    cache_dir.mkdir()

    # Set old mtime so it would be deleted
    old_time = time.time() - CACHE_MAX_AGE_SECONDS - 3600
    os.utime(cache_dir, (old_time, old_time))

    # Mock shutil.rmtree to raise PermissionError
    def mock_rmtree(_path: Path) -> None:
        raise PermissionError

    with (
        patch(
            "clan_lib.nix.cache_cleanup.clan_tmp_dir",
            return_value=clean_cache_dir.parent,
        ),
        patch("clan_lib.nix.cache_cleanup.shutil.rmtree", mock_rmtree),
    ):
        # Should not raise, just log the error
        _cleanup_old_cache_dirs()

    # Directory still exists because rmtree was mocked to fail
    assert cache_dir.exists()


def test_cleanup_removes_directory_contents(clean_cache_dir: Path) -> None:
    """Test that cleanup removes directories including their contents."""
    # Create an old directory with files inside
    old_dir = clean_cache_dir / "old_hash_with_contents"
    old_dir.mkdir()

    # Create some symlinks inside (simulating cached packages)
    (old_dir / "git").symlink_to("/nix/store/fake-git-path")
    (old_dir / "openssh").symlink_to("/nix/store/fake-openssh-path")

    # Set old mtime
    old_time = time.time() - CACHE_MAX_AGE_SECONDS - 3600
    os.utime(old_dir, (old_time, old_time))

    with patch(
        "clan_lib.nix.cache_cleanup.clan_tmp_dir", return_value=clean_cache_dir.parent
    ):
        _cleanup_old_cache_dirs()

    assert not old_dir.exists(), "Old directory and contents should be removed"
