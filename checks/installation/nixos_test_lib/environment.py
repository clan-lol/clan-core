"""Environment setup utilities for VM tests"""

import os


def setup_nix_environment(temp_dir: str, closure_info: str) -> None:
    """Set up nix chroot store environment"""
    if "NIX_REMOTE" in os.environ:
        del os.environ["NIX_REMOTE"]  # we don't have any nix daemon running

    os.environ["TMPDIR"] = temp_dir
    # Set NIX_CONFIG globally to disable substituters for speed
    os.environ["NIX_CONFIG"] = "substituters = \ntrusted-public-keys = "
