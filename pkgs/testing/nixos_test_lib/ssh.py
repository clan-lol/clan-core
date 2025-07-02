"""SSH and test setup utilities"""

import subprocess
from pathlib import Path
from typing import NamedTuple

from .nix_setup import setup_nix_in_nix
from .port import find_free_port, setup_port_forwarding


class TestEnvironment(NamedTuple):
    host_port: int
    ssh_key: str
    flake_dir: str


def setup_test_environment(
    target,
    temp_dir: str,
    closure_info: str,
    assets_ssh_privkey: str,
    clan_core_for_checks: str,
) -> TestEnvironment:
    """Set up common test environment including SSH, port forwarding, and flake setup

    Returns:
        TestEnvironment with host_port, ssh_key, and flake_dir
    """
    # Run setup function
    setup_nix_in_nix(closure_info)

    host_port = find_free_port()
    target.wait_for_unit("sshd.service")
    target.wait_for_open_port(22)

    setup_port_forwarding(target, host_port)

    ssh_key = Path(temp_dir) / "id_ed25519"
    with ssh_key.open("w") as f, Path(assets_ssh_privkey).open() as src:
        f.write(src.read())
    ssh_key.chmod(0o600)

    # Copy test flake to temp directory
    flake_dir = Path(temp_dir) / "test-flake"
    subprocess.run(["cp", "-r", clan_core_for_checks, flake_dir], check=True)  # noqa: S603, S607
    subprocess.run(["chmod", "-R", "+w", flake_dir], check=True)  # noqa: S603, S607

    return TestEnvironment(host_port, str(ssh_key), str(flake_dir))
