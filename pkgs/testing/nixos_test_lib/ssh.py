"""SSH and test setup utilities"""

from pathlib import Path
from typing import NamedTuple

from .port import find_free_port, setup_port_forwarding


class SSHConnection(NamedTuple):
    host_port: int
    ssh_key: str


def setup_ssh_connection(
    target,
    temp_dir: str,
    assets_ssh_privkey: str,
) -> SSHConnection:
    """Set up SSH connection with port forwarding to test VM

    Args:
        target: Test VM target
        temp_dir: Temporary directory for SSH key
        assets_ssh_privkey: Path to SSH private key asset

    Returns:
        SSHConnection with host_port and ssh_key path
    """
    host_port = find_free_port()
    target.wait_for_unit("sshd.service")
    target.wait_for_open_port(22)

    setup_port_forwarding(target, host_port)

    ssh_key = Path(temp_dir) / "id_ed25519"
    with ssh_key.open("w") as f, Path(assets_ssh_privkey).open() as src:
        f.write(src.read())
    ssh_key.chmod(0o600)

    return SSHConnection(host_port, str(ssh_key))
