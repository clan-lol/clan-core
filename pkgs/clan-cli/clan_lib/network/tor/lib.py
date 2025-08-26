#!/usr/bin/env python3

import logging
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from subprocess import Popen

from clan_lib.errors import ClanError
from clan_lib.nix import nix_shell

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class TorTarget:
    onion: str
    port: int


def is_tor_running(proxy_port: int | None = None) -> bool:
    """Checks if Tor is online."""
    if proxy_port is None:
        proxy_port = 9050
    try:
        tor_online_test(proxy_port)
    except ClanError as err:
        log.debug(f"Tor is not running: {err}")
        return False

    return True


# TODO: Move this to network technology tor module
@contextmanager
def spawn_tor() -> Iterator[None]:
    """Spawns a Tor process using `nix-shell` if Tor is not already running."""
    # Check if Tor is already running
    if is_tor_running():
        log.info("Tor is running")
        return
    cmd_args = ["tor", "--HardwareAccel", "1"]
    packages = ["tor"]
    cmd = nix_shell(packages, cmd_args)
    try:
        process = Popen(cmd)
        try:
            while not is_tor_running():
                log.debug("Waiting for Tor to start...")
                time.sleep(0.2)
            log.info("Tor is now running")
            yield
        finally:
            log.info("Terminating Tor process...")
            process.terminate()
            process.wait()
            log.info("Tor process terminated")
    except OSError as e:
        msg = f"Failed to spawn tor process with command: {cmd}"
        raise ClanError(msg) from e


@dataclass(frozen=True)
class TorCheck:
    onion: str
    expected_content: str
    port: int = 80


def tor_online_test(proxy_port: int) -> None:
    """Tests if Tor is online by checking if we can establish a SOCKS5 connection."""
    import socket

    # Try to establish a SOCKS5 handshake with the Tor proxy
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.0)  # Short timeout for local connection

    try:
        # Connect to the SOCKS5 proxy
        sock.connect(("localhost", proxy_port))

        # Send SOCKS5 handshake
        sock.sendall(b"\x05\x01\x00")  # SOCKS5, 1 auth method, no auth
        response = sock.recv(2)

        # Check if we got a valid SOCKS5 response
        if response == b"\x05\x00":  # SOCKS5, no auth accepted
            return
        msg = f"Invalid SOCKS5 response from Tor: {response.hex()}"
        raise ClanError(msg)

    except (TimeoutError, ConnectionRefusedError, OSError) as e:
        msg = f"Cannot connect to Tor SOCKS5 proxy at localhost:{proxy_port}: {e}"
        raise ClanError(msg) from e
    finally:
        sock.close()
