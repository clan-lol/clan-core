import time
from pathlib import Path

from clan_lib.nix import run


def invalidate_flake_cache(flake_path: Path) -> None:
    """Force flake cache invalidation by modifying the git repository.

    This adds a dummy file to git which changes the NAR hash of the flake,
    forcing a cache invalidation.
    """
    dummy_file = flake_path / f".cache_invalidation_{time.time()}"
    dummy_file.write_text("invalidate")
    run(["git", "add", str(dummy_file)])
