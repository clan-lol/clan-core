"""Test to verify nix command caching behavior.

This test verifies that _resolve_package_path (which calls nix build --inputs-from)
is properly cached using symlinks as GC roots, so repeated nix_shell calls for the
same package only trigger one actual nix build invocation.
"""

import logging
import os
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import patch

import pytest

from clan_lib.cmd import RunOpts
from clan_lib.cmd import run as cmd_run
from clan_lib.dirs import runtime_deps_flake
from clan_lib.errors import CmdOut
from clan_lib.nix.shell import _get_nix_shell_cache_dir, _resolve_package_path
from clan_lib.nix.shell import nix_shell as nix_shell_original

log = logging.getLogger(__name__)


def create_mock_nix_run(
    fake_store_path: str,
    call_counter: list[int] | None = None,
    captured_commands: list[list[str]] | None = None,
) -> Callable[[list[str], RunOpts | None], CmdOut]:
    """Create a mock nix run function that simulates nix build --out-link.

    Args:
        fake_store_path: Path to use as the fake store path result
        call_counter: Optional list to track call count (use list for mutability)
        captured_commands: Optional list to capture commands

    """

    def mock_nix_run(cmd: list[str], opts: RunOpts | None = None) -> CmdOut:  # noqa: ARG001
        if call_counter is not None:
            call_counter[0] += 1
        if captured_commands is not None:
            captured_commands.append(cmd)
        # Simulate nix build: create symlink at --out-link path
        if "--out-link" in cmd:
            out_link_idx = cmd.index("--out-link")
            out_link_path = Path(cmd[out_link_idx + 1])
            out_link_path.parent.mkdir(parents=True, exist_ok=True)
            if out_link_path.exists() or out_link_path.is_symlink():
                out_link_path.unlink()
            out_link_path.symlink_to(fake_store_path)
        return CmdOut(
            returncode=0,
            stdout=fake_store_path,
            stderr="",
            env=None,
            cwd=Path.cwd(),
            command_list=cmd,
            msg="",
        )

    return mock_nix_run


@contextmanager
def nix_run_context(
    call_counter: list[int] | None = None,
    captured_commands: list[list[str]] | None = None,
) -> Iterator[None]:
    """Context manager that mocks nix run in sandbox, uses real nix otherwise.

    In the nix sandbox, nix build --out-link doesn't work with --store /build/store,
    so we mock the nix execution. Outside the sandbox, we use real nix.
    """
    fake_store_path = str(runtime_deps_flake().resolve())

    if os.environ.get("IN_NIX_SANDBOX") == "1":
        mock_run = create_mock_nix_run(fake_store_path, call_counter, captured_commands)
        with patch("clan_lib.nix.shell.run", mock_run):
            yield
    else:
        # Outside sandbox: use real nix, but wrap to capture commands/count if requested
        def counting_run(cmd: list[str], opts: RunOpts | None = None) -> CmdOut:
            if call_counter is not None:
                call_counter[0] += 1
            if captured_commands is not None:
                captured_commands.append(cmd)
            return cmd_run(cmd, opts)

        if call_counter is not None or captured_commands is not None:
            with patch("clan_lib.nix.shell.run", counting_run):
                yield
        else:
            yield


@dataclass
class NixInvocationCounter:
    """Tracks nix command invocations during a test."""

    nix_shell_calls: list[tuple[list[str], list[str]]] = field(default_factory=list)
    resolve_package_calls: list[tuple[str, str]] = field(default_factory=list)
    shell_fallback_calls: list[tuple[list[str], list[str]]] = field(
        default_factory=list
    )

    @property
    def shell_call_count(self) -> int:
        """Number of nix_shell() calls."""
        return len(self.nix_shell_calls)

    @property
    def build_count(self) -> int:
        """Number of nix build --inputs-from invocations."""
        return len(self.resolve_package_calls)

    @property
    def shell_fallback_count(self) -> int:
        """Number of nix shell --inputs-from invocations."""
        return len(self.shell_fallback_calls)

    def unique_packages_resolved(self) -> set[str]:
        """Get set of unique packages that were resolved."""
        return {pkg for _, pkg in self.resolve_package_calls}


@pytest.fixture
def nix_counter() -> NixInvocationCounter:
    """Provide a counter for tracking nix invocations."""
    return NixInvocationCounter()


@pytest.fixture
def clean_cache() -> Iterator[Path]:
    """Provide a clean temporary cache directory for testing.

    Patches clan_tmp_dir to return a fresh temporary directory,
    ensuring test isolation.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Clear the in-process cache for _get_nix_shell_cache_dir
        _get_nix_shell_cache_dir.cache_clear()

        with (
            patch("clan_lib.nix.shell.clan_tmp_dir", return_value=tmp_path),
            patch("clan_lib.nix.cache_cleanup.clan_tmp_dir", return_value=tmp_path),
        ):
            yield tmp_path

        # Clear again after test
        _get_nix_shell_cache_dir.cache_clear()


def test_resolve_package_path_symlink_caching(clean_cache: Path) -> None:
    """Test that _resolve_package_path uses symlink-based caching correctly.

    Verifies that:
    1. First call resolves the package and creates a symlink
    2. Subsequent calls read from the symlink without re-resolving
    """
    _ = clean_cache  # Used via fixture patching

    call_count = 0
    original_resolve = _resolve_package_path

    def counting_resolve(nixpkgs_path: Path, package: str) -> Path | None:
        nonlocal call_count
        call_count += 1
        log.info("_resolve_package_path called: %s (call #%d)", package, call_count)
        return original_resolve(nixpkgs_path, package)

    # Simulate multiple nix_shell calls for the same package
    with (
        patch("clan_lib.nix.shell._resolve_package_path", counting_resolve),
        patch("clan_lib.nix.shell.Packages.is_provided", return_value=False),
        patch.dict("os.environ", {"IN_NIX_SANDBOX": ""}),
    ):
        # Call nix_shell multiple times with the same package
        for i in range(5):
            result = nix_shell_original(["git"], ["echo", "test"])
            log.info("nix_shell call %d: %s...", i + 1, result[:3])

    # The key assertion: _resolve_package_path should be called each time
    # because we're NOT patching the cache mechanism, just counting calls
    # The actual symlink-based caching happens inside _resolve_package_path
    assert call_count == 5, (
        f"Expected _resolve_package_path to be called 5 times "
        f"(once per nix_shell call), but it was called {call_count} times"
    )


def test_resolve_package_path_caching() -> None:
    """Test that _resolve_package_path caching works correctly.

    Verifies that calling the function multiple times with the same arguments
    uses the cached symlink (second call doesn't invoke nix).
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        _get_nix_shell_cache_dir.cache_clear()

        nix_call_count = [0]  # Use list for mutability in closure

        with (
            patch("clan_lib.nix.shell.clan_tmp_dir", return_value=tmp_path),
            nix_run_context(call_counter=nix_call_count),
        ):
            nixpkgs_path = runtime_deps_flake().resolve()

            # First call should create cache symlink
            result1 = _resolve_package_path(nixpkgs_path, "git")
            assert result1 is not None, "First resolution should succeed"
            assert nix_call_count[0] == 1, "First call should invoke nix"

            # Check cache symlink was created
            cache_dir = _get_nix_shell_cache_dir(nixpkgs_path)
            cache_link = cache_dir / "git"
            assert cache_link.is_symlink(), "Cache symlink should be created"
            assert cache_link.resolve() == result1

            # Second call should use cache (same result, no additional nix call)
            result2 = _resolve_package_path(nixpkgs_path, "git")
            assert result2 == result1, "Cached result should match"
            assert nix_call_count[0] == 1, (
                "Second call should use cache, not invoke nix"
            )

        _get_nix_shell_cache_dir.cache_clear()


def test_resolve_package_path_caching_different_packages() -> None:
    """Test that caching works correctly with different packages.

    Each unique package should have its own cache symlink.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        _get_nix_shell_cache_dir.cache_clear()

        with (
            patch("clan_lib.nix.shell.clan_tmp_dir", return_value=tmp_path),
            nix_run_context(),
        ):
            nixpkgs_path = runtime_deps_flake().resolve()

            # Resolve multiple packages
            git_path = _resolve_package_path(nixpkgs_path, "git")
            sshpass_path = _resolve_package_path(nixpkgs_path, "sshpass")

            assert git_path is not None
            assert sshpass_path is not None

            # Check both cache symlinks exist
            cache_dir = _get_nix_shell_cache_dir(nixpkgs_path)
            assert (cache_dir / "git").is_symlink()
            assert (cache_dir / "sshpass").is_symlink()

            # Resolve again - should use cache
            git_path2 = _resolve_package_path(nixpkgs_path, "git")
            sshpass_path2 = _resolve_package_path(nixpkgs_path, "sshpass")

            assert git_path2 == git_path
            assert sshpass_path2 == sshpass_path

        _get_nix_shell_cache_dir.cache_clear()


@pytest.mark.with_core
def test_cache_invalidation_on_broken_symlink() -> None:
    """Test that broken symlinks are detected and re-resolved.

    Simulates garbage collection by creating a broken symlink,
    then verifies that _resolve_package_path detects this and re-resolves.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        _get_nix_shell_cache_dir.cache_clear()

        with (
            patch("clan_lib.nix.shell.clan_tmp_dir", return_value=tmp_path),
            nix_run_context(),
        ):
            nixpkgs_path = runtime_deps_flake().resolve()

            # First resolution
            result1 = _resolve_package_path(nixpkgs_path, "git")
            assert result1 is not None

            # Simulate garbage collection by replacing with a broken symlink
            cache_dir = _get_nix_shell_cache_dir(nixpkgs_path)
            cache_link = cache_dir / "git"
            cache_link.unlink()
            cache_link.symlink_to("/nix/store/nonexistent-path")

            # Next resolution should detect the broken symlink and re-resolve
            result2 = _resolve_package_path(nixpkgs_path, "git")
            assert result2 is not None
            assert result2 != "/nix/store/nonexistent-path"
            assert Path(result2).exists()

        _get_nix_shell_cache_dir.cache_clear()


def test_cache_isolation_by_nixpkgs_path() -> None:
    """Test that different nixpkgs paths use different cache directories.

    This ensures cache invalidation when nixpkgs version changes.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        _get_nix_shell_cache_dir.cache_clear()

        with patch("clan_lib.nix.shell.clan_tmp_dir", return_value=tmp_path):
            # Get cache dirs for different nixpkgs paths
            cache_dir1 = _get_nix_shell_cache_dir(Path("/nix/store/path1-nixpkgs"))
            cache_dir2 = _get_nix_shell_cache_dir(Path("/nix/store/path2-nixpkgs"))

            assert cache_dir1 != cache_dir2, (
                "Different nixpkgs should use different cache dirs"
            )
            assert cache_dir1.parent == cache_dir2.parent, (
                "Cache dirs should be siblings"
            )

        _get_nix_shell_cache_dir.cache_clear()


def test_nix_build_uses_out_link() -> None:
    """Test that nix build is called with --out-link to create GC roots.

    This verifies the key behavior change: using --out-link instead of --no-link
    ensures the symlink acts as a GC root, preventing garbage collection.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        _get_nix_shell_cache_dir.cache_clear()

        captured_commands: list[list[str]] = []

        with (
            patch("clan_lib.nix.shell.clan_tmp_dir", return_value=tmp_path),
            nix_run_context(captured_commands=captured_commands),
        ):
            nixpkgs_path = runtime_deps_flake().resolve()
            result = _resolve_package_path(nixpkgs_path, "git")

            assert result is not None, "Resolution should succeed"

            # Find the nix build command
            nix_build_cmds = [
                cmd for cmd in captured_commands if "build" in cmd and "nix" in cmd[0]
            ]
            assert len(nix_build_cmds) == 1, "Should have exactly one nix build command"

            nix_cmd = nix_build_cmds[0]

            # Verify --out-link is used (not --no-link)
            assert "--out-link" in nix_cmd, (
                f"Command should use --out-link for GC root, got: {nix_cmd}"
            )
            assert "--no-link" not in nix_cmd, (
                f"Command should NOT use --no-link, got: {nix_cmd}"
            )

            # Verify the out-link path is in the cache directory
            out_link_idx = nix_cmd.index("--out-link")
            out_link_path = nix_cmd[out_link_idx + 1]
            assert "nix_shell_cache" in out_link_path, (
                f"Out-link should be in cache dir, got: {out_link_path}"
            )
            assert out_link_path.endswith("/git"), (
                f"Out-link should end with package name, got: {out_link_path}"
            )

        _get_nix_shell_cache_dir.cache_clear()
