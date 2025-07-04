"""Port management utilities for NixOS installation tests."""

import socket
import time
from typing import Any


class PortUtilsError(Exception):
    """Port utils related errors."""


def find_free_port() -> int:
    """Find a free port on the host."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def check_host_port_open(port: int) -> bool:
    """Verify port forwarding is working by checking if the host port is listening."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(("localhost", port))
            return result == 0
    except OSError as e:
        print(f"Port check failed: {e}")
        return False


def setup_port_forwarding(target: Any, host_port: int) -> None:
    """Set up port forwarding and wait for it to be ready."""
    print(f"Setting up port forwarding from host port {host_port} to guest port 22")
    target.forward_port(host_port=host_port, guest_port=22)

    # Give the port forwarding time to establish
    time.sleep(2)

    # Wait up to 30 seconds for the port to become available
    port_ready = False
    for i in range(30):
        if check_host_port_open(host_port):
            port_ready = True
            print(f"Host port {host_port} is now listening")
            break
        print(f"Waiting for host port {host_port} to be ready... attempt {i + 1}/30")
        time.sleep(1)

    if not port_ready:
        msg = f"Host port {host_port} never became available for forwarding"
        raise PortUtilsError(msg)
