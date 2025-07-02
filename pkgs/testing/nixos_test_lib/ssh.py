"""SSH and test setup utilities"""

import subprocess
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

    ssh_key = os.path.join(temp_dir, "id_ed25519")
    with open(ssh_key, "w") as f:
        with open(assets_ssh_privkey) as src:
            f.write(src.read())
    os.chmod(ssh_key, 0o600)

    # Copy test flake to temp directory
    flake_dir = os.path.join(temp_dir, "test-flake")
    subprocess.run(["cp", "-r", clan_core_for_checks, flake_dir], check=True)
    subprocess.run(["chmod", "-R", "+w", flake_dir], check=True)

    return TestEnvironment(host_port, ssh_key, flake_dir)
