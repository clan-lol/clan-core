"""Generate ZeroTier identities, networks, and compute IPs.

Modes:
  network    -- generate identity + network ID + IP
  identity   -- generate a new identity, derive IP from an existing network-id
  compute-ip -- pure computation: derive IP from existing identity + network-id
"""

import argparse
import secrets
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from zerotier_tools import Identity, ZToolError, compute_zerotier_ip


def create_identity() -> Identity:
    with TemporaryDirectory() as d:
        tmpdir = Path(d)
        private = tmpdir / "identity.secret"
        public = tmpdir / "identity.public"
        subprocess.run(["zerotier-idtool", "generate", private, public], check=True)
        return Identity.from_directory(tmpdir)


def create_network_id(node_id: str) -> str:
    """Generate a ZeroTier network ID: {node_id}{6 random hex chars}.

    The suffix must not be all zeros (reserved by ZeroTier).
    See EmbeddedNetworkController.cpp in the ZeroTier source.
    """
    while True:
        suffix = secrets.token_hex(3)
        if suffix != "000000":
            return node_id + suffix


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["network", "identity", "compute-ip"],
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
            identity = create_identity()
            network_id = create_network_id(identity.node_id())
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
        case "compute-ip":
            if args.network_id_file is None:
                msg = "--network-id-file parameter is required in compute-ip mode"
                raise ZToolError(msg)
            identity = Identity.from_secret_file(args.identity_secret)
            network_id = args.network_id_file.read_text().strip()
            ip = compute_zerotier_ip(network_id, identity.node_id())
            args.ip.write_text(ip.compressed)
        case _:
            msg = f"unknown mode {args.mode}"
            raise ZToolError(msg)


if __name__ == "__main__":
    main()
