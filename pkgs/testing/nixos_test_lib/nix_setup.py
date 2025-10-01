"""Nix store setup utilities for VM tests"""

import os
import subprocess
from pathlib import Path

# These paths will be substituted during package build
CP_BIN = "@cp@"
NIX_STORE_BIN = "@nix-store@"
XARGS_BIN = "@xargs@"


def setup_nix_in_nix(temp_dir: str, closure_info: str | None) -> None:
    """Set up Nix store inside test environment

    Args:
        temp_dir: Temporary directory
        closure_info: Path to closure info directory containing store-paths file,
            or None if no closure info
    """
    # Remove NIX_REMOTE if present (we don't have any nix daemon running)
    if "NIX_REMOTE" in os.environ:
        del os.environ["NIX_REMOTE"]

    # Set NIX_CONFIG globally to disable substituters for speed
    os.environ["NIX_CONFIG"] = "substituters = \ntrusted-public-keys = "

    # Set up environment variables for test environment
    os.environ["HOME"] = str(temp_dir)
    os.environ["NIX_STATE_DIR"] = f"{temp_dir}/nix"
    os.environ["NIX_CONF_DIR"] = f"{temp_dir}/etc"
    os.environ["IN_NIX_SANDBOX"] = "1"
    os.environ["CLAN_TEST_STORE"] = f"{temp_dir}/store"
    os.environ["LOCK_NIX"] = f"{temp_dir}/nix_lock"

    # Create necessary directories
    Path(f"{temp_dir}/nix").mkdir(parents=True, exist_ok=True)
    Path(f"{temp_dir}/etc").mkdir(parents=True, exist_ok=True)
    Path(f"{temp_dir}/store").mkdir(parents=True, exist_ok=True)
    Path(f"{temp_dir}/store/nix/store").mkdir(parents=True, exist_ok=True)
    Path(f"{temp_dir}/store/nix/var/nix/gcroots").mkdir(parents=True, exist_ok=True)

    # Set up Nix store if closure info is provided
    if closure_info and Path(closure_info).exists():
        store_paths_file = Path(closure_info) / "store-paths"
        if store_paths_file.exists():
            # Use xargs with parallel processing to copy store paths efficiently
            # --reflink=auto enables copy-on-write when filesystem supports it
            # -P uses all available CPU cores for parallel copying
            num_cpus = str(os.cpu_count() or 1)
            with store_paths_file.open() as f:
                subprocess.run(  # noqa: S603
                    [
                        XARGS_BIN,
                        "-r",
                        f"-P{num_cpus}",  # Use all available CPUs
                        CP_BIN,
                        "--no-dereference",
                        "--recursive",
                        "--reflink=auto",  # Use copy-on-write if available
                        "--target-directory",
                        f"{temp_dir}/store/nix/store",
                    ],
                    stdin=f,
                    check=True,
                )

            # Load Nix database
            registration_file = Path(closure_info) / "registration"
            if registration_file.exists():
                with registration_file.open() as f:
                    subprocess.run(  # noqa: S603
                        [NIX_STORE_BIN, "--load-db", "--store", f"{temp_dir}/store"],
                        input=f.read(),
                        text=True,
                        check=True,
                    )


def prepare_test_flake(
    temp_dir: str, clan_core_for_checks: str, closure_info: str
) -> Path:
    """Set up Nix store and copy test flake to temporary directory

    Args:
        temp_dir: Temporary directory
        clan_core_for_checks: Path to clan-core-for-checks
        closure_info: Path to closure info for Nix store setup

    Returns:
        Path to the test flake directory
    """
    # Set up Nix store
    setup_nix_in_nix(temp_dir, closure_info)

    # Copy test flake
    flake_dir = Path(temp_dir) / "test-flake"
    subprocess.run(["cp", "-r", clan_core_for_checks, flake_dir], check=True)  # noqa: S603, S607
    subprocess.run(["chmod", "-R", "+w", flake_dir], check=True)  # noqa: S603, S607
    return flake_dir
