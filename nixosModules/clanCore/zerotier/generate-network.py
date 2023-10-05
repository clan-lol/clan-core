import argparse
import contextlib
import json
import socket
import subprocess
import time
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterator, Optional


class ClanError(Exception):
    pass


def try_bind_port(port: int) -> bool:
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    with tcp, udp:
        try:
            tcp.bind(("127.0.0.1", port))
            udp.bind(("127.0.0.1", port))
            return True
        except OSError:
            return False


def try_connect_port(port: int) -> bool:
    sock = socket.socket(socket.AF_INET)
    result = sock.connect_ex(("127.0.0.1", port))
    sock.close()
    return result == 0


def find_free_port() -> Optional[int]:
    """Find an unused localhost port from 1024-65535 and return it."""
    with contextlib.closing(socket.socket(type=socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class ZerotierController:
    def __init__(self, port: int, home: Path) -> None:
        self.port = port
        self.home = home
        self.authtoken = (home / "authtoken.secret").read_text()
        self.secret = (home / "identity.secret").read_text()

    def _http_request(
        self,
        path: str,
        method: str = "GET",
        headers: dict[str, str] = {},
        data: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        body = None
        headers = headers.copy()
        if data is not None:
            body = json.dumps(data).encode("ascii")
            headers["Content-Type"] = "application/json"
        headers["X-ZT1-AUTH"] = self.authtoken
        url = f"http://127.0.0.1:{self.port}{path}"
        req = urllib.request.Request(url, headers=headers, method=method, data=body)
        resp = urllib.request.urlopen(req)
        return json.load(resp)

    def status(self) -> dict[str, Any]:
        return self._http_request("/status")

    def create_network(self, data: dict[str, Any] = {}) -> dict[str, Any]:
        identity = (self.home / "identity.public").read_text()
        node_id = identity.split(":")[0]
        return self._http_request(
            f"/controller/network/{node_id}______", method="POST", data=data
        )

    def get_network(self, id: str) -> dict[str, Any]:
        return self._http_request(f"/controller/network/{id}")


@contextmanager
def zerotier_controller() -> Iterator[ZerotierController]:
    # This check could be racy but it's unlikely in practice
    controller_port = find_free_port()
    if controller_port is None:
        raise ClanError("cannot find a free port for zerotier controller")

    with TemporaryDirectory() as d:
        tempdir = Path(d)
        home = tempdir / "zerotier-one"
        home.mkdir()
        cmd = [
            "fakeroot",
            "--",
            "zerotier-one",
            f"-p{controller_port}",
            str(home),
        ]
        with subprocess.Popen(cmd) as p:
            try:
                print(
                    f"wait for controller to be started on 127.0.0.1:{controller_port}...",
                )
                while not try_connect_port(controller_port):
                    status = p.poll()
                    if status is not None:
                        raise ClanError(
                            f"zerotier-one has been terminated unexpected with {status}"
                        )
                    time.sleep(0.1)
                print()

                yield ZerotierController(controller_port, home)
            finally:
                p.kill()
                p.wait()


# TODO: allow merging more network configuration here
def create_network() -> dict:
    with zerotier_controller() as controller:
        network = controller.create_network()
        return {
            "secret": controller.secret,
            "networkid": network["nwid"],
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("network_id")
    parser.add_argument("identity_secret")
    args = parser.parse_args()

    zerotier = create_network()
    Path(args.network_id).write_text(zerotier["networkid"])
    Path(args.identity_secret).write_text(zerotier["secret"])


if __name__ == "__main__":
    main()
