import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from zerotier_tools import Identity, ZToolError, compute_zerotier_ip

# Package root so subprocess invocations can find zerotier_tools.
PACKAGE_ROOT = str(Path(__file__).parent.parent)

# Synthetic identity in zerotier format: node_id:0:public_part:secret_part
SAMPLE_SECRET = (
    "a1b2c3d4e5:0:"
    "0000000000000000000000000000000000000000000000000000000000000000"
    "1111111111111111111111111111111111111111111111111111111111111111:"
    "2222222222222222222222222222222222222222222222222222222222222222"
    "3333333333333333333333333333333333333333333333333333333333333333"
)
SAMPLE_NODE_ID = "a1b2c3d4e5"

NETWORK_A = "1111111111111111"
NETWORK_B = "2222222222222222"

has_zerotier_idtool = shutil.which("zerotier-idtool") is not None


@pytest.fixture
def identity(tmp_path: Path) -> Identity:
    secret_file = tmp_path / "identity.secret"
    secret_file.write_text(SAMPLE_SECRET)
    return Identity.from_secret_file(secret_file)


def run_generate(*args: str, **kwargs: Any) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "zerotier_tools.generate", *args],
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "PYTHONPATH": PACKAGE_ROOT},
        **kwargs,
    )


class TestIdentity:
    def test_from_secret_file_parses_node_id(self, identity: Identity) -> None:
        assert identity.node_id() == SAMPLE_NODE_ID

    def test_from_secret_file_preserves_private(self, identity: Identity) -> None:
        assert identity.private == SAMPLE_SECRET

    def test_from_secret_file_agrees_with_directory_constructor(
        self, tmp_path: Path
    ) -> None:
        """Both constructors produce the same node_id for the same identity."""
        parts = SAMPLE_SECRET.split(":")
        (tmp_path / "identity.secret").write_text(SAMPLE_SECRET)
        (tmp_path / "identity.public").write_text(":".join(parts[:3]))

        from_dir = Identity.from_directory(tmp_path)
        from_file = Identity.from_secret_file(tmp_path / "identity.secret")

        assert from_dir.node_id() == from_file.node_id()
        assert from_dir.public == from_file.public


class TestComputeZerotierIp:
    def test_golden_values(self, identity: Identity) -> None:
        """Pin known (identity, network) -> IP mappings as regression guard."""
        assert (
            compute_zerotier_ip(NETWORK_A, identity.node_id()).compressed
            == "fd11:1111:1111:1111:1199:93a1:b2c3:d4e5"
        )
        assert (
            compute_zerotier_ip(NETWORK_B, identity.node_id()).compressed
            == "fd22:2222:2222:2222:2299:93a1:b2c3:d4e5"
        )

    def test_different_networks_yield_different_ips(self, identity: Identity) -> None:
        """Same identity on two networks produces different IPs."""
        ip_a = compute_zerotier_ip(NETWORK_A, identity.node_id())
        ip_b = compute_zerotier_ip(NETWORK_B, identity.node_id())
        assert ip_a != ip_b

    def test_embeds_network_and_node(self, identity: Identity) -> None:
        """Verify the IP encodes network_id in bytes 1-8 and node_id in bytes 11-15."""
        ip = compute_zerotier_ip(NETWORK_A, identity.node_id())
        packed = ip.packed

        assert packed[0] == 0xFD

        nwid = int(NETWORK_A, 16)
        for i in range(8):
            assert packed[1 + i] == (nwid >> (56 - 8 * i)) & 0xFF

        assert packed[9] == 0x99
        assert packed[10] == 0x93

        node_id = int(SAMPLE_NODE_ID, 16)
        for i in range(5):
            assert packed[11 + i] == (node_id >> (32 - 8 * i)) & 0xFF

    def test_rejects_short_network_id(self, identity: Identity) -> None:
        with pytest.raises(ZToolError, match="must be 16 characters"):
            compute_zerotier_ip("abc123", identity.node_id())

    def test_rejects_long_network_id(self, identity: Identity) -> None:
        with pytest.raises(ZToolError, match="must be 16 characters"):
            compute_zerotier_ip("79fadafbe98c5dd8ff", identity.node_id())


@pytest.mark.skipif(not has_zerotier_idtool, reason="zerotier-idtool not in PATH")
class TestCliIdentityMode:
    def test_generates_identity_and_derives_ip(self, tmp_path: Path) -> None:
        network_id_file = tmp_path / "network-id"
        network_id_file.write_text(NETWORK_A)

        ip_output = tmp_path / "zerotier-ip"
        secret_output = tmp_path / "zerotier-identity-secret"

        result = run_generate(
            "--mode",
            "identity",
            "--identity-secret",
            str(secret_output),
            "--network-id-file",
            str(network_id_file),
            "--ip",
            str(ip_output),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert secret_output.exists()
        assert ip_output.exists()

        identity = Identity.from_secret_file(secret_output)
        expected_ip = compute_zerotier_ip(NETWORK_A, identity.node_id())
        assert ip_output.read_text() == expected_ip.compressed

    def test_fails_without_network_id_file(self, tmp_path: Path) -> None:
        result = run_generate(
            "--mode",
            "identity",
            "--identity-secret",
            str(tmp_path / "secret"),
            "--ip",
            str(tmp_path / "ip"),
        )
        assert result.returncode != 0


class TestCliComputeIpMode:
    def test_writes_correct_output(self, tmp_path: Path, identity: Identity) -> None:
        secret_file = tmp_path / "identity.secret"
        secret_file.write_text(SAMPLE_SECRET)

        network_id_file = tmp_path / "network-id"
        network_id_file.write_text(NETWORK_A)

        ip_output = tmp_path / "zerotier-ip"

        result = run_generate(
            "--mode",
            "compute-ip",
            "--identity-secret",
            str(secret_file),
            "--network-id-file",
            str(network_id_file),
            "--ip",
            str(ip_output),
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"

        expected_ip = compute_zerotier_ip(NETWORK_A, identity.node_id())
        assert ip_output.read_text() == expected_ip.compressed

    def test_does_not_overwrite_identity(self, tmp_path: Path) -> None:
        secret_file = tmp_path / "identity.secret"
        secret_file.write_text(SAMPLE_SECRET)

        network_id_file = tmp_path / "network-id"
        network_id_file.write_text(NETWORK_A)

        run_generate(
            "--mode",
            "compute-ip",
            "--identity-secret",
            str(secret_file),
            "--network-id-file",
            str(network_id_file),
            "--ip",
            str(tmp_path / "zerotier-ip"),
        )
        assert secret_file.read_text() == SAMPLE_SECRET

    def test_fails_without_network_id_file(self, tmp_path: Path) -> None:
        secret_file = tmp_path / "identity.secret"
        secret_file.write_text(SAMPLE_SECRET)

        result = run_generate(
            "--mode",
            "compute-ip",
            "--identity-secret",
            str(secret_file),
            "--ip",
            str(tmp_path / "zerotier-ip"),
        )
        assert result.returncode != 0
