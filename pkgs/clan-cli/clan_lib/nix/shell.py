import logging
import os
from functools import cache
from hashlib import sha256
from pathlib import Path

from clan_lib.cmd import Log, RunOpts, run
from clan_lib.dirs import clan_tmp_dir, runtime_deps_flake
from clan_lib.errors import ClanCmdError
from clan_lib.nix import Packages, nix_command
from clan_lib.nix.cache_cleanup import maybe_cleanup_cache

log = logging.getLogger(__name__)


@cache
def _get_nix_shell_cache_dir(nixpkgs_path: Path) -> Path:
    """Get the cache directory for nix shell store paths.

    The cache directory is based on a hash of the nixpkgs path, so it
    automatically invalidates when nixpkgs changes.

    Args:
        nixpkgs_path: Resolved nixpkgs flake path

    Returns:
        Path to the cache directory

    """
    hashed = sha256(str(nixpkgs_path).encode()).hexdigest()[:16]
    cache_dir = Path(clan_tmp_dir()) / "nix_shell_cache" / hashed
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Touch the directory to update mtime (marks it as "recently used")
    cache_dir.touch(exist_ok=True)

    return cache_dir


def _resolve_package_path(nixpkgs_path: Path, package: str) -> Path | None:
    """Resolve and cache a package's store path.

    Uses symlinks as both cache and GC roots. The symlink is created by
    nix build --out-link, which prevents the garbage collector from removing
    the store path as long as the symlink exists.

    The cache is stored in clan_tmp_dir() and keyed by nixpkgs_path hash.

    Args:
        nixpkgs_path: Resolved nixpkgs flake path (used as cache key component)
        package: Package name (e.g., "git")

    Returns:
        Store path string, or None if resolution fails

    """
    cache_dir = _get_nix_shell_cache_dir(nixpkgs_path)
    cache_link = cache_dir / package

    # Check if we have a cached symlink that points to an existing store path
    if cache_link.is_symlink():
        store_path = cache_link.resolve()
        if Path(store_path).exists():
            # Touch parent dir to mark as recently used
            cache_dir.touch(exist_ok=True)
            return store_path
        # Symlink is broken (store path was garbage collected), remove it
        log.debug("Cached store path for %s no longer exists, re-resolving", package)
        cache_link.unlink(missing_ok=True)

    # Resolve the package and create symlink as GC root
    cmd = nix_command(
        [
            "build",
            "--inputs-from",
            str(nixpkgs_path),
            f"nixpkgs#{package}",
            "--print-out-paths",
            "--out-link",
            str(cache_link),
        ]
    )
    try:
        proc = run(cmd, RunOpts(log=Log.NONE, check=True))
        store_path = Path(proc.stdout.strip())
    except ClanCmdError:
        log.warning("Failed to resolve package %s", package)
        return None

    if not store_path or not Path(store_path).exists():
        log.warning("Resolved empty or non-existent store path for %s", package)
        return None

    return store_path


def _nix_shell_fallback(
    packages: list[str],
    cmd: list[str],
) -> list[str]:
    """Fall back to nix shell for packages that couldn't be resolved.

    Args:
        packages: Package names from nixpkgs (without nixpkgs# prefix)
        cmd: Command to wrap

    Returns:
        Command list prefixed with nix shell invocation

    """
    return [
        *nix_command(["shell", "--inputs-from", f"{runtime_deps_flake()!s}"]),
        *[f"nixpkgs#{pkg}" for pkg in packages],
        "-c",
        *cmd,
    ]


#   Features:
#     - allow list for programs (need to be specified in allowed-packages.json)
#     - be abe to compute a closure of all deps for testing
#     - build clan distributions that ship some or all packages (eg. clan-cli-full)
def nix_shell(packages: list[str], cmd: list[str]) -> list[str]:
    """Wrap a command with nix shell for required packages.

    Uses cached store paths when available for improved performance.
    Falls back to nix shell for packages that cannot be resolved.

    Args:
        packages: List of package names (e.g., "git", "openssh")
        cmd: Command to wrap

    Returns:
        Command list, either with PATH modification or nix shell wrapper

    """
    for program in packages:
        Packages.ensure_allowed(program)

    if os.environ.get("IN_NIX_SANDBOX"):
        return cmd

    missing_packages = [pkg for pkg in packages if not Packages.is_provided(pkg)]

    if not missing_packages:
        return cmd

    # Lazy cleanup: runs at most once per hour per process
    maybe_cleanup_cache()

    # Try to resolve packages via cache
    nixpkgs_path = runtime_deps_flake().resolve()

    resolved_paths: list[Path] = []
    for pkg in missing_packages:
        path = _resolve_package_path(nixpkgs_path, pkg)
        if path is None:
            # Fall back to nix shell for all packages
            return _nix_shell_fallback(missing_packages, cmd)
        resolved_paths.append(path)

    # All packages resolved - use PATH modification
    path_additions = [str(p / "bin") for p in resolved_paths]
    current_path = os.environ.get("PATH", "")
    new_path = os.pathsep.join([*path_additions, current_path])

    return ["env", f"PATH={new_path}", *cmd]
