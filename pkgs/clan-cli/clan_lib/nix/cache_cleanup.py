"""Nix shell cache management with age-based cleanup.

The cache stores symlinks in clan_tmp_dir()/nix_shell_cache/<nixpkgs_hash>/<package>.
These symlinks act as GC roots - store paths won't be collected until symlinks are removed.

Cache cleanup is lazy: it runs at most once per CLEANUP_CHECK_INTERVAL when
nix_shell() is called, and uses exclusive file locking to prevent race conditions
when multiple clan instances run concurrently.
"""

import logging
import os
import shutil
import time
from pathlib import Path

from clan_lib.dirs import clan_tmp_dir
from clan_lib.locked_open import locked_open

log = logging.getLogger(__name__)

# Cache cleanup configuration
CACHE_MAX_AGE_DAYS = int(os.environ.get("CLAN_CACHE_MAX_AGE_DAYS", "7"))
CACHE_MAX_AGE_SECONDS = CACHE_MAX_AGE_DAYS * 24 * 60 * 60
CLEANUP_CHECK_INTERVAL = 3600  # Check at most once per hour

_last_cleanup_check: float = 0.0


def _cleanup_old_cache_dirs() -> None:
    """Remove cache directories older than CACHE_MAX_AGE_DAYS.

    Uses exclusive file locking to prevent race conditions when
    multiple clan instances run concurrently.
    """
    cache_base = Path(clan_tmp_dir()) / "nix_shell_cache"
    if not cache_base.exists():
        return

    now = time.time()
    lock_file = cache_base / ".cleanup.lock"

    # Ensure lock file exists
    lock_file.touch(exist_ok=True)

    try:
        with locked_open(lock_file, "r") as _:
            for cache_dir in cache_base.iterdir():
                if cache_dir.name.startswith("."):
                    continue  # Skip lock file and hidden files
                if not cache_dir.is_dir():
                    continue

                # Check directory age using mtime
                try:
                    dir_age = now - cache_dir.stat().st_mtime
                    if dir_age > CACHE_MAX_AGE_SECONDS:
                        log.debug(
                            "Removing old cache dir: %s (age: %.1f days)",
                            cache_dir,
                            dir_age / 86400,
                        )
                        shutil.rmtree(cache_dir)
                except OSError as e:
                    log.debug("Failed to check/remove cache dir %s: %s", cache_dir, e)
    except OSError as e:
        log.debug("Failed to acquire cleanup lock: %s", e)


def maybe_cleanup_cache() -> None:
    """Trigger cache cleanup if enough time has passed since last check.

    This function is safe to call frequently - it will only perform actual
    cleanup at most once per CLEANUP_CHECK_INTERVAL (default: 1 hour).
    """
    global _last_cleanup_check  # noqa: PLW0603

    now = time.time()
    if now - _last_cleanup_check > CLEANUP_CHECK_INTERVAL:
        _last_cleanup_check = now
        _cleanup_old_cache_dirs()
