#!/usr/bin/env python3

import contextlib
import socket
from collections.abc import Callable

import pytest


def _unused_port(socket_type: int) -> int:
    """Find an unused localhost port from 1024-65535 and return it."""
    with contextlib.closing(socket.socket(type=socket_type)) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


PortFunction = Callable[[], int]


@pytest.fixture(scope="session")
def unused_tcp_port() -> PortFunction:
    """A function, producing different unused TCP ports."""
    produced = set()

    def factory() -> int:
        """Return an unused port."""
        port = _unused_port(socket.SOCK_STREAM)

        while port in produced:
            port = _unused_port(socket.SOCK_STREAM)

        produced.add(port)

        return port

    return factory


@pytest.fixture(scope="session")
def unused_udp_port() -> PortFunction:
    """A function, producing different unused UDP ports."""
    produced = set()

    def factory() -> int:
        """Return an unused port."""
        port = _unused_port(socket.SOCK_DGRAM)

        while port in produced:
            port = _unused_port(socket.SOCK_DGRAM)

        produced.add(port)

        return port

    return factory
