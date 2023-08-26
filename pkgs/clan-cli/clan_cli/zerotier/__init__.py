import json
import socket
import subprocess
import time
import urllib.request
from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Iterator, Optional

from ..errors import ClanError
from ..nix import nix_shell, unfree_nix_shell


def try_bind_port(port: int) -> bool:
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    with tcp, udp:
        try:
            tcp.bind(("127.0.0.1", port))
            udp.bind(("127.0.0.1", port))
            return True
        except socket.error:
            return False


def try_connect_port(port: int) -> bool:
    sock = socket.socket(socket.AF_INET)
    result = sock.connect_ex(("127.0.0.1", port))
    sock.close()
    return result == 0


def find_free_port(port_range: range) -> Optional[int]:
    for port in port_range:
        if try_bind_port(port):
            return port
    return None


class ZerotierController:
    def __init__(self, port: int, home: Path) -> None:
        self.port = port
        self.home = home
        self.secret = (home / "authtoken.secret").read_text()

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
        headers["X-ZT1-AUTH"] = self.secret
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

    def update_network(self, id: str, new_config: dict[str, Any]) -> dict[str, Any]:
        return self._http_request(
            f"/controller/network/{id}", method="POST", data=new_config
        )


@contextmanager
def zerotier_controller() -> Iterator[ZerotierController]:
    # This check could be racy but it's unlikely in practice
    controller_port = find_free_port(range(10000, 65535))
    if controller_port is None:
        raise ClanError("cannot find a free port for zerotier controller")

    cmd = unfree_nix_shell(
        ["bash", "zerotierone"], ["bash", "-c", "command -v zerotier-one"]
    )
    res = subprocess.run(
        cmd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    zerotier_exe = res.stdout.strip()
    if zerotier_exe is None:
        raise ClanError("cannot find zerotier-one executable")

    if not zerotier_exe.startswith("/nix/store"):
        raise ClanError(
            f"zerotier-one executable needs to come from /nix/store: {zerotier_exe}"
        )
    with TemporaryDirectory() as d:
        tempdir = Path(d)
        home = tempdir / "zerotier-one"
        home.mkdir()
        cmd = nix_shell(
            ["bubblewrap"],
            [
                "bwrap",
                "--proc",
                "/proc",
                "--dev",
                "/dev",
                "--uid",
                "0",
                "--gid",
                "0",
                "--ro-bind",
                "/nix",
                "/nix",
                "--bind",
                str(home),
                "/var/lib/zerotier-one",
                zerotier_exe,
                f"-p{controller_port}",
            ],
        )
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


class ZerotierNetwork:
    def __init__(self, network_id: str) -> None:
        self.network_id = network_id


# TODO: allow merging more network configuration here
def create_network(private: bool = False) -> ZerotierNetwork:
    with zerotier_controller() as controller:
        network = controller.create_network()
        network_id = network["nwid"]
        network = controller.get_network(network_id)
        network["private"] = private
        network["v6AssignMode"]["rfc4193"] = True
        controller.update_network(network_id, network)
        # TODO: persist home into sops?
        return ZerotierNetwork(network_id)
