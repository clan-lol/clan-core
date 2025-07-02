"""Nix store setup utilities for VM tests"""

import os
import shutil
import subprocess
from pathlib import Path


def setup_nix_in_nix(closure_info: str) -> None:
    """Set up Nix store inside test environment

    Args:
        closure_info: Path to closure info directory containing store-paths file
    """
    tmpdir = Path(os.environ.get("TMPDIR", "/tmp"))

    # Remove NIX_REMOTE if present (we don't have any nix daemon running)
    if "NIX_REMOTE" in os.environ:
        del os.environ["NIX_REMOTE"]

    # Set NIX_CONFIG globally to disable substituters for speed
    os.environ["NIX_CONFIG"] = "substituters = \ntrusted-public-keys = "

    # Set up environment variables for test environment
    os.environ["HOME"] = tmpdir
    os.environ["NIX_STATE_DIR"] = f"{tmpdir}/nix"
    os.environ["NIX_CONF_DIR"] = f"{tmpdir}/etc"
    os.environ["IN_NIX_SANDBOX"] = "1"
    os.environ["CLAN_TEST_STORE"] = f"{tmpdir}/store"
    os.environ["LOCK_NIX"] = f"{tmpdir}/nix_lock"

    # Create necessary directories
    Path(f"{tmpdir}/nix").mkdir(parents=True, exist_ok=True)
    Path(f"{tmpdir}/etc").mkdir(parents=True, exist_ok=True)
    Path(f"{tmpdir}/store").mkdir(parents=True, exist_ok=True)

    # Set up Nix store if closure info is provided
    if closure_info and Path(closure_info).exists():
        store_paths_file = Path(closure_info) / "store-paths"
        if store_paths_file.exists():
            with store_paths_file.open() as f:
                store_paths = f.read().strip().split("\n")

            # Copy store paths to test store
            for store_path in store_paths:
                if store_path.strip():
                    dest_path = f"{tmpdir}/store{store_path}"
                    if not os.path.exists(dest_path):
                        # Create parent directories
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        # Copy the store path
                        if os.path.isdir(store_path):
                            shutil.copytree(store_path, dest_path, dirs_exist_ok=True)
                        else:
                            shutil.copy2(store_path, dest_path)

            # Load Nix database
            registration_file = Path(closure_info) / "registration"
            if registration_file.exists():
                env = os.environ.copy()
                env["NIX_REMOTE"] = f"local?store={tmpdir}/store"

                with registration_file.open() as f:
                    subprocess.run(
                        ["nix-store", "--load-db"],
                        input=f.read(),
                        text=True,
                        env=env,
                        check=True,
                    )
