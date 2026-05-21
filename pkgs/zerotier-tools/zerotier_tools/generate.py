"""Generate ZeroTier identities, networks, and compute IPs.

Modes:
  network   -- spin up a temporary controller, create a network, output identity + network-id + IP
  identity  -- generate a new identity, derive IP from an existing network-id
"""

import argparse
import contextlib
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from zerotier_tools import Identity, ZToolError, compute_zerotier_ip


class ZerotierController:
    def __init__(self, port: int, home: Path) -> None:
        self.port = port
        self.home = home
        self.authtoken = (home / "authtoken.secret").read_text()
        self.identity = Identity.from_directory(home)

    def _http_request(
        self,
        path: str,
        method: str = "GET",
        headers: dict[str, str] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if headers is None:
            headers = {}
        body = None
        headers = headers.copy()
        if data is not None:
            body = json.dumps(data).encode("ascii")
            headers["Content-Type"] = "application/json"
        headers["X-ZT1-AUTH"] = self.authtoken
        url = f"http://127.0.0.1:{self.port}{path}"
        # Safe: only connecting to localhost zerotier API
        req = urllib.request.Request(url, headers=headers, method=method, data=body)  # noqa: S310
        with urllib.request.urlopen(req, timeout=5) as resp:  # noqa: S310
            return json.load(resp)

    def status(self) -> dict[str, Any]:
        return self._http_request("/status")

    def create_network(self, data: dict[str, Any] | None = None) -> dict[str, Any]:
        if data is None:
            data = {}
        return self._http_request(
            f"/controller/network/{self.identity.node_id()}______",
            method="POST",
            data=data,
        )

    def get_network(self, network_id: str) -> dict[str, Any]:
        return self._http_request(f"/controller/network/{network_id}")


def _try_connect_port(port: int) -> bool:
    sock = socket.socket(socket.AF_INET)
    result = sock.connect_ex(("127.0.0.1", port))
    sock.close()
    return result == 0


def _find_free_port() -> int | None:
    with contextlib.closing(socket.socket(type=socket.SOCK_STREAM)) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextmanager
def zerotier_controller() -> Iterator[ZerotierController]:
    # This check could be racy but it's unlikely in practice
    controller_port = _find_free_port()
    if controller_port is None:
        msg = "cannot find a free port for zerotier controller"
        raise ZToolError(msg)

    with TemporaryDirectory() as d:
        tempdir = Path(d)
        home = tempdir / "zerotier-one"
        home.mkdir()
        cmd = [
            "zerotier-one",
            f"-p{controller_port}",
            str(home),
        ]

        with subprocess.Popen(cmd, start_new_session=True) as p:
            process_group = os.getpgid(p.pid)
            try:
                print(
                    f"wait for controller to be started on 127.0.0.1:{controller_port}...",
                )
                while not _try_connect_port(controller_port):
                    status = p.poll()
                    if status is not None:
                        msg = (
                            f"zerotier-one has been terminated unexpected with {status}"
                        )
                        raise ZToolError(msg)
                    time.sleep(0.1)

                zt_controller = ZerotierController(controller_port, home)

                # Wait for the controller API to be fully ready,
                # not just the port being open
                for _ in range(50):
                    try:
                        zt_controller.status()
                        break
                    except OSError as err:
                        status = p.poll()
                        if status is not None:
                            msg = f"zerotier-one has been terminated unexpected with {status}"
                            raise ZToolError(msg) from err
                        time.sleep(0.1)
                else:
                    msg = "zerotier controller API did not become ready in time"
                    raise ZToolError(msg)

                print()

                yield zt_controller
            finally:
                os.killpg(process_group, signal.SIGKILL)


@dataclass
class NetworkController:
    networkid: str
    identity: Identity


def create_network_controller() -> NetworkController:
    last_err: Exception | None = None
    for _ in range(10):
        try:
            with zerotier_controller() as controller:
                network = controller.create_network()
                return NetworkController(network["nwid"], controller.identity)
        except (ZToolError, urllib.error.HTTPError, urllib.error.URLError) as err:
            print(f"failed to create network ({err}), retrying...", file=sys.stderr)
            last_err = err
    msg = "failed to create ZeroTier network after 10 attempts"
    raise ZToolError(msg) from last_err


def create_identity() -> Identity:
    with TemporaryDirectory() as d:
        tmpdir = Path(d)
        private = tmpdir / "identity.secret"
        public = tmpdir / "identity.public"
        subprocess.run(["zerotier-idtool", "generate", private, public], check=True)
        return Identity.from_directory(tmpdir)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["network", "identity"],
        required=True,
        type=str,
    )
    parser.add_argument("--ip", type=Path, required=True)
    parser.add_argument("--identity-secret", type=Path, required=True)
    parser.add_argument("--network-id", type=str, required=False)
    parser.add_argument("--network-id-file", type=Path, required=False)
    args = parser.parse_args()

    match args.mode:
        case "network":
            if args.network_id is None:
                msg = "--network-id parameter is required in network mode"
                raise ZToolError(msg)
            controller = create_network_controller()
            identity = controller.identity
            network_id = controller.networkid
            Path(args.network_id).write_text(network_id)
            ip = compute_zerotier_ip(network_id, identity.node_id())
            args.identity_secret.write_text(identity.private)
            args.ip.write_text(ip.compressed)
        case "identity":
            if args.network_id_file is None:
                msg = "--network-id-file parameter is required in identity mode"
                raise ZToolError(msg)
            identity = create_identity()
            network_id = args.network_id_file.read_text().strip()
            ip = compute_zerotier_ip(network_id, identity.node_id())
            args.identity_secret.write_text(identity.private)
            args.ip.write_text(ip.compressed)
        case _:
            msg = f"unknown mode {args.mode}"
            raise ZToolError(msg)


if __name__ == "__main__":
    main()
