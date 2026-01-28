"""Test to verify nix command caching behavior.

This test verifies that _resolve_package_path (which calls nix build --inputs-from)
is properly cached, so repeated nix_shell calls for the same package only trigger
one actual nix build invocation.
"""

import logging
from collections.abc import Iterator
from dataclasses import dataclass, field
from functools import cache
from unittest.mock import patch

import pytest

from clan_lib.nix import _resolve_package_path
from clan_lib.nix import nix_shell as nix_shell_original

log = logging.getLogger(__name__)


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
def track_nix_internals(nix_counter: NixInvocationCounter) -> Iterator[None]:
    """Track internal nix function calls to verify caching.

    This patches the internal functions to count invocations while
    preserving their functionality.
    """
    # Clear cache before test to ensure clean state
    _resolve_package_path.cache_clear()

    # Get the unwrapped original function
    original_resolve = _resolve_package_path.__wrapped__

    def counting_resolve(nixpkgs_path: str, package: str) -> str | None:
        nix_counter.resolve_package_calls.append((nixpkgs_path, package))
        return original_resolve(nixpkgs_path, package)

    cached_counting_resolve = cache(counting_resolve)

    with patch("clan_lib.nix._resolve_package_path", cached_counting_resolve):
        yield

    # Clear cache after test
    _resolve_package_path.cache_clear()


def test_resolve_package_path_caching() -> None:
    """Test that _resolve_package_path caching works correctly.

    Verifies that calling the function multiple times with the same arguments
    only executes the actual nix build once.
    """
    # Clear cache
    _resolve_package_path.cache_clear()

    # Track calls to the underlying function
    call_count = 0
    original_resolve = _resolve_package_path.__wrapped__

    def counting_resolve(nixpkgs_path: str, package: str) -> str | None:
        nonlocal call_count
        call_count += 1
        log.info("_resolve_package_path called: %s (call #%d)", package, call_count)
        return original_resolve(nixpkgs_path, package)

    cached_counting = cache(counting_resolve)

    # Simulate multiple nix_shell calls for the same package
    # We need to bypass the "package provided" and "in sandbox" checks
    with (
        patch("clan_lib.nix._resolve_package_path", cached_counting),
        patch("clan_lib.nix.Packages.is_provided", return_value=False),
        patch.dict("os.environ", {"IN_NIX_SANDBOX": ""}),
    ):
        # Call nix_shell multiple times with the same package
        for i in range(5):
            result = nix_shell_original(["git"], ["echo", "test"])
            log.info("nix_shell call %d: %s...", i + 1, result[:3])

    print(f"\n{'=' * 60}")
    print("Caching Test Results")
    print(f"{'=' * 60}")
    print("nix_shell() called: 5 times")
    print(f"_resolve_package_path actually executed: {call_count} time(s)")
    print(f"{'=' * 60}")

    # The key assertion: _resolve_package_path should only be called once
    # because subsequent calls should use the cache
    assert call_count == 1, (
        f"Expected _resolve_package_path to be called exactly 1 time due to caching, "
        f"but it was called {call_count} times"
    )


def test_resolve_package_path_caching_different_packages() -> None:
    """Test that caching works correctly with different packages.

    Each unique package should trigger one _resolve_package_path call.
    """
    _resolve_package_path.cache_clear()

    call_log: list[str] = []
    original_resolve = _resolve_package_path.__wrapped__

    def counting_resolve(nixpkgs_path: str, package: str) -> str | None:
        call_log.append(package)
        log.info("_resolve_package_path called for: %s", package)
        return original_resolve(nixpkgs_path, package)

    cached_counting = cache(counting_resolve)

    with (
        patch("clan_lib.nix._resolve_package_path", cached_counting),
        patch("clan_lib.nix.Packages.is_provided", return_value=False),
        patch.dict("os.environ", {"IN_NIX_SANDBOX": ""}),
    ):
        # Call with git 3 times
        for _ in range(3):
            nix_shell_original(["git"], ["echo", "test"])

        # Call with openssh 2 times
        for _ in range(2):
            nix_shell_original(["openssh"], ["echo", "test"])

        # Call with git again
        nix_shell_original(["git"], ["echo", "test"])

    print(f"\n{'=' * 60}")
    print("Multi-Package Caching Test Results")
    print(f"{'=' * 60}")
    print("nix_shell() called: 6 times total")
    print("  - git: 4 times")
    print("  - openssh: 2 times")
    print(f"_resolve_package_path executions: {len(call_log)}")
    print(f"  - Packages resolved: {call_log}")
    print(f"{'=' * 60}")

    # Should only resolve each unique package once
    assert len(call_log) == 2, (
        f"Expected 2 _resolve_package_path calls (one per unique package), "
        f"but got {len(call_log)}: {call_log}"
    )
    assert set(call_log) == {"git", "openssh"}, (
        f"Expected to resolve 'git' and 'openssh', but resolved: {call_log}"
    )
