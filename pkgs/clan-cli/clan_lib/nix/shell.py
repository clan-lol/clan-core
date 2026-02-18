import json
import logging
import os
import shutil
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from pathlib import Path

from clan_lib.cmd import run
from clan_lib.dirs import clan_tmp_dir, runtime_deps_flake
from clan_lib.errors import ClanError
from clan_lib.nix import current_system, nix_build, nix_command
from clan_lib.nix.cache_cleanup import maybe_cleanup_cache

log = logging.getLogger(__name__)


@dataclass
class ResolvedPackage:
    """Information about a resolved package."""

    store_path: Path
    exe_name: str


# lazy loads list of allowed and static programs
class Packages:
    allowed_packages: set[str] | None = None
    static_packages: set[str] | None = None

    @classmethod
    def ensure_allowed(cls: type["Packages"], package: str) -> None:
        if cls.allowed_packages is None:
            with (Path(__file__).parent / "allowed-packages.json").open() as f:
                cls.allowed_packages = allowed_packages = set(json.load(f))
        else:
            allowed_packages = cls.allowed_packages

        if package not in allowed_packages:
            msg = f"Package not allowed: '{package}', allowed packages are:\n{'\n'.join(allowed_packages)}"
            raise ClanError(msg)

    @classmethod
    def is_provided(cls: type["Packages"], program: str) -> bool:
        """Determines if a program is shipped with the clan package."""
        if cls.static_packages is None:
            cls.static_packages = set(
                os.environ.get("CLAN_PROVIDED_PACKAGES", "").split(":"),
            )

        if program in cls.static_packages:
            if shutil.which(program) is None:
                log.warning(
                    f"Program {program} is not in the path even though it should be shipped with clan"
                )
                return False
            return True
        return False


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


def _create_gcroot(package: str, nixpkgs_path: Path, gcroot_path: Path) -> None:
    """Create a GC root symlink for a package.

    This function is separated out to allow mocking/tracking in tests.

    Args:
        package: Package name (e.g., "git")
        nixpkgs_path: Path to nixpkgs flake (for --inputs-from)
        gcroot_path: Path where the GC root symlink should be created

    """
    cmd = nix_build(
        [f"nixpkgs#{package}"], inputs_from=nixpkgs_path, gcroot=gcroot_path
    )
    run(cmd)


def _resolve_package(nixpkgs_path: Path, package: str) -> ResolvedPackage | None:
    """Resolve and cache a package's store path and executable name.

    Uses symlinks as both cache and GC roots. The symlink prevents the garbage
    collector from removing the store path as long as the symlink exists.

    The cache is stored in clan_tmp_dir() and keyed by nixpkgs_path hash.

    Args:
        nixpkgs_path: Resolved nixpkgs flake path (used as cache key component)
        package: Package name (e.g., "git")

    Returns:
        ResolvedPackage with store path and executable name, or None if resolution fails

    """
    # Use Flake.select to get package info
    # Import here to avoid circular import with clan_lib.nix
    from clan_lib.flake.flake import Flake  # noqa: PLC0415

    nixpkgs = Flake(str(nixpkgs_path))
    system = current_system()
    pkg_prefix = f"inputs.nixpkgs.legacyPackages.{system}.{package}"

    # Precache both selectors in one nix evaluation
    nixpkgs.precache(
        [
            f"{pkg_prefix}.outPath",
            f"{pkg_prefix}.?meta.?mainProgram",
            f"{pkg_prefix}.?meta.?outputsToInstall",
        ]
    )

    cache_dir = _get_nix_shell_cache_dir(nixpkgs_path)
    cache_links = [cache_dir / package]
    outputs_to_install_result = nixpkgs.select(f"{pkg_prefix}.?meta.?outputsToInstall")
    # The selector returns {"meta": {"outputsToInstall": [...]}} so extract the list
    outputs_to_install = None
    if isinstance(outputs_to_install_result, dict):
        outputs_to_install = outputs_to_install_result.get("meta", {}).get(
            "outputsToInstall"
        )
    if outputs_to_install:
        cache_links = [
            cache_dir / f"{package}-{output}" for output in outputs_to_install
        ]

    # Base path for nix build --out-link (nix adds -<output> suffixes automatically)
    cache_link_base = cache_dir / package

    # Check if all cached symlinks point to existing store paths
    all_links_valid = cache_links and all(
        link.is_symlink() and link.resolve().exists() for link in cache_links
    )

    # Get mainProgram from meta (cached by precache), fall back to package name
    meta_result = nixpkgs.select(f"{pkg_prefix}.?meta.?mainProgram")
    if meta_result and "meta" in meta_result and "mainProgram" in meta_result["meta"]:
        exe_name = meta_result["meta"]["mainProgram"]
    else:
        exe_name = package

    if all_links_valid:
        # Use the first link's store path (primary output)
        store_path = cache_links[0].resolve()
        cache_dir.touch(exist_ok=True)
        return ResolvedPackage(store_path=store_path, exe_name=exe_name)

    # Some or all symlinks are broken/missing, clean up and re-resolve
    if any(link.exists() or link.is_symlink() for link in cache_links):
        log.debug(f"Cached store path for {package} no longer valid, re-resolving")
        for link in cache_links:
            link.unlink(missing_ok=True)

    out_path = nixpkgs.select(f"{pkg_prefix}.outPath")
    if not out_path:
        log.warning(f"Package {package} has no outPath")
        return None

    store_path = Path(out_path)

    # Create GC root symlink
    _create_gcroot(package, nixpkgs_path, cache_link_base)

    return ResolvedPackage(store_path=store_path, exe_name=exe_name)


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

    resolved: list[ResolvedPackage] = []
    for pkg in missing_packages:
        result = _resolve_package(nixpkgs_path, pkg)
        if result is None:
            # Fall back to nix shell for all packages
            return _nix_shell_fallback(missing_packages, cmd)
        resolved.append(result)

    # All packages resolved - use PATH modification
    path_additions = [str(r.store_path / "bin") for r in resolved]
    current_path = os.environ.get("PATH", "")
    new_path = os.pathsep.join([*path_additions, current_path])

    return ["env", f"PATH={new_path}", *cmd]
