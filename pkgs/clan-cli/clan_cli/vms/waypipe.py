import contextlib
import socket
import subprocess
import time
from collections.abc import Iterator

from ..errors import ClanError
from ..nix import nix_shell

VMADDR_CID_HYPERVISOR = 2


def test_vsock_port(port: int) -> bool:
    try:
        s = socket.socket(socket.AF_VSOCK, socket.SOCK_STREAM)
        s.connect((VMADDR_CID_HYPERVISOR, port))
        s.close()
        return True
    except OSError:
        return False


@contextlib.contextmanager
def start_waypipe(cid: int | None, title_prefix: str) -> Iterator[None]:
    if cid is None:
        yield
        return
    waypipe = nix_shell(
        ["nixpkgs#waypipe"],
        [
            "waypipe",
            "--vsock",
            "--socket",
            f"s{cid}:3049",
            "--title-prefix",
            title_prefix,
            "client",
        ],
    )
    with subprocess.Popen(waypipe) as proc:
        try:
            while not test_vsock_port(3049):
                rc = proc.poll()
                if rc is not None:
                    msg = f"waypipe exited unexpectedly with code {rc}"
                    raise ClanError(msg)
                time.sleep(0.1)
            yield
        finally:
            proc.kill()
