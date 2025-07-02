"""Nix store setup utilities for VM tests"""

import os
import subprocess
from pathlib import Path

# These paths will be substituted during package build
CP_BIN = "@cp@"
NIX_STORE_BIN = "@nix-store@"
XARGS_BIN = "@xargs@"


def setup_nix_in_nix(closure_info: str | None) -> None:
    """Set up Nix store inside test environment

    Args:
        closure_info: Path to closure info directory containing store-paths file,
            or None if no closure info
    """
    tmpdir = Path(os.environ.get("TMPDIR", "/tmp"))  # noqa: S108

    # Remove NIX_REMOTE if present (we don't have any nix daemon running)
    if "NIX_REMOTE" in os.environ:
        del os.environ["NIX_REMOTE"]

    # Set NIX_CONFIG globally to disable substituters for speed
    os.environ["NIX_CONFIG"] = "substituters = \ntrusted-public-keys = "

    # Set up environment variables for test environment
    os.environ["HOME"] = str(tmpdir)
    os.environ["NIX_STATE_DIR"] = f"{tmpdir}/nix"
    os.environ["NIX_CONF_DIR"] = f"{tmpdir}/etc"
    os.environ["IN_NIX_SANDBOX"] = "1"
    os.environ["CLAN_TEST_STORE"] = f"{tmpdir}/store"
    os.environ["LOCK_NIX"] = f"{tmpdir}/nix_lock"

    # Create necessary directories
    Path(f"{tmpdir}/nix").mkdir(parents=True, exist_ok=True)
    Path(f"{tmpdir}/etc").mkdir(parents=True, exist_ok=True)
    Path(f"{tmpdir}/store").mkdir(parents=True, exist_ok=True)
    Path(f"{tmpdir}/store/nix/store").mkdir(parents=True, exist_ok=True)
    Path(f"{tmpdir}/store/nix/var/nix/gcroots").mkdir(parents=True, exist_ok=True)

    # Set up Nix store if closure info is provided
    if closure_info and Path(closure_info).exists():
        store_paths_file = Path(closure_info) / "store-paths"
        if store_paths_file.exists():
            # Use xargs to handle potentially long lists of store paths
            # Equivalent to: xargs cp --recursive --target-directory
            # "$CLAN_TEST_STORE/nix/store" < "$closureInfo/store-paths"
            with store_paths_file.open() as f:
                subprocess.run(  # noqa: S603
                    [
                        XARGS_BIN,
                        CP_BIN,
                        "--recursive",
                        "--target-directory",
                        f"{tmpdir}/store/nix/store",
                    ],
                    stdin=f,
                    check=True,
                )

            # Load Nix database
            registration_file = Path(closure_info) / "registration"
            if registration_file.exists():
                with registration_file.open() as f:
                    subprocess.run(  # noqa: S603
                        [NIX_STORE_BIN, "--load-db", "--store", f"{tmpdir}/store"],
                        input=f.read(),
                        text=True,
                        check=True,
                    )
