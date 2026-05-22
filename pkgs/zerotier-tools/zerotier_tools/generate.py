"""Generate ZeroTier identities, networks, and compute IPs.

Modes:
  network       -- generate identity + network ID + IP (legacy, kept for compat)
  identity      -- generate a new identity, derive IP from an existing network-id (legacy)
  identity-only -- generate a new identity keypair (no IP, no network-id needed)
  network-id    -- derive a network ID from an existing identity
  compute-ip    -- pure computation: derive IP from existing identity + network-id
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


def _require(args: argparse.Namespace, name: str, mode: str) -> None:
    if getattr(args, name, None) is None:
        msg = f"--{name.replace('_', '-')} is required in {mode} mode"
        raise ZToolError(msg)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["network", "identity", "identity-only", "network-id", "compute-ip"],
        required=True,
        type=str,
    )
    parser.add_argument("--ip", type=Path, required=False)
    parser.add_argument("--identity-secret", type=Path, required=False)
    parser.add_argument("--identity-secret-file", type=Path, required=False)
    parser.add_argument("--network-id", type=str, required=False)
    parser.add_argument("--network-id-file", type=Path, required=False)
    args = parser.parse_args()

    match args.mode:
        case "network":
            _require(args, "identity_secret", args.mode)
            _require(args, "network_id", args.mode)
            _require(args, "ip", args.mode)
            identity = create_identity()
            network_id = create_network_id(identity.node_id())
            Path(args.network_id).write_text(network_id)
            ip = compute_zerotier_ip(network_id, identity.node_id())
            args.identity_secret.write_text(identity.private)
            args.ip.write_text(ip.compressed)
        case "identity":
            _require(args, "identity_secret", args.mode)
            _require(args, "network_id_file", args.mode)
            _require(args, "ip", args.mode)
            identity = create_identity()
            network_id = args.network_id_file.read_text().strip()
            ip = compute_zerotier_ip(network_id, identity.node_id())
            args.identity_secret.write_text(identity.private)
            args.ip.write_text(ip.compressed)
        case "identity-only":
            _require(args, "identity_secret", args.mode)
            identity = create_identity()
            args.identity_secret.write_text(identity.private)
        case "network-id":
            _require(args, "identity_secret_file", args.mode)
            _require(args, "network_id", args.mode)
            identity = Identity.from_secret_file(args.identity_secret_file)
            network_id = create_network_id(identity.node_id())
            Path(args.network_id).write_text(network_id)
        case "compute-ip":
            _require(args, "identity_secret", args.mode)
            _require(args, "network_id_file", args.mode)
            _require(args, "ip", args.mode)
            identity = Identity.from_secret_file(args.identity_secret)
            network_id = args.network_id_file.read_text().strip()
            ip = compute_zerotier_ip(network_id, identity.node_id())
            args.ip.write_text(ip.compressed)
        case _:
            msg = f"unknown mode {args.mode}"
            raise ZToolError(msg)


if __name__ == "__main__":
    main()
