import argparse
import ipaddress
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

# Constants
NODE_ID_LENGTH = 10
NETWORK_ID_LENGTH = 16


class ClanError(Exception):
    pass


class Identity:
    def __init__(self, secret: str) -> None:
        self.private = secret.strip()

    def node_id(self) -> str:
        nid = self.private.split(":")[0]
        if len(nid) != NODE_ID_LENGTH:
            msg = f"node_id must be {NODE_ID_LENGTH} characters long, got {len(nid)}: {nid}"
            raise ClanError(msg)
        return nid


@dataclass
class NetworkController:
    networkid: str
    identity: Identity


def load_or_create_identity(identity_secret_path: Path) -> Identity:
    if identity_secret_path.exists():
        return Identity(identity_secret_path.read_text())
    with TemporaryDirectory() as d:
        tmpdir = Path(d)
        private = tmpdir / "identity.secret"
        public = tmpdir / "identity.public"
        subprocess.run(["zerotier-idtool", "generate", private, public], check=True)
        return Identity(private.read_text())


def create_network_controller(identity_secret_path: Path) -> NetworkController:
    identity = load_or_create_identity(identity_secret_path)
    network_id = f"{identity.node_id()}000001"
    return NetworkController(network_id, identity)


def create_identity(identity_secret_path: Path) -> Identity:
    return load_or_create_identity(identity_secret_path)


def compute_zerotier_ip(network_id: str, identity: Identity) -> ipaddress.IPv6Address:
    if len(network_id) != NETWORK_ID_LENGTH:
        msg = f"network_id must be {NETWORK_ID_LENGTH} characters long, got '{network_id}'"
        raise ClanError(msg)
    nwid = int(network_id, 16)
    node_id = int(identity.node_id(), 16)
    addr_parts = bytearray(
        [
            0xFD,
            (nwid >> 56) & 0xFF,
            (nwid >> 48) & 0xFF,
            (nwid >> 40) & 0xFF,
            (nwid >> 32) & 0xFF,
            (nwid >> 24) & 0xFF,
            (nwid >> 16) & 0xFF,
            (nwid >> 8) & 0xFF,
            (nwid) & 0xFF,
            0x99,
            0x93,
            (node_id >> 32) & 0xFF,
            (node_id >> 24) & 0xFF,
            (node_id >> 16) & 0xFF,
            (node_id >> 8) & 0xFF,
            (node_id) & 0xFF,
        ],
    )
    return ipaddress.IPv6Address(bytes(addr_parts))


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
    args = parser.parse_args()

    match args.mode:
        case "network":
            if args.network_id is None:
                msg = "network_id parameter is required"
                raise ClanError(msg)
            controller = create_network_controller(args.identity_secret)
            identity = controller.identity
            network_id = controller.networkid
            Path(args.network_id).write_text(network_id)
        case "identity":
            if args.network_id is None:
                msg = "network_id parameter is required"
                raise ClanError(msg)
            identity = create_identity(args.identity_secret)
            network_id = args.network_id
        case _:
            msg = f"unknown mode {args.mode}"
            raise ClanError(msg)
    ip = compute_zerotier_ip(network_id, identity)

    args.identity_secret.write_text(identity.private)
    args.ip.write_text(ip.compressed)


if __name__ == "__main__":
    main()
