"""Tests for Tor hidden service address detection."""

from __future__ import annotations

from typing import TYPE_CHECKING
from unittest.mock import patch

import network_status

if TYPE_CHECKING:
    from pathlib import Path


class TestReadOnionAddress:
    def test_reads_valid_onion_address(self, tmp_path: Path) -> None:
        f = tmp_path / "hostname"
        f.write_text("abc123def456.onion\n")
        assert network_status.read_onion_address(f) == "abc123def456.onion"

    def test_returns_none_for_non_onion(self, tmp_path: Path) -> None:
        f = tmp_path / "hostname"
        f.write_text("not-an-onion-address\n")
        assert network_status.read_onion_address(f) is None

    def test_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        assert network_status.read_onion_address(tmp_path / "nonexistent") is None

    def test_does_not_match_onion_substring_in_middle(self, tmp_path: Path) -> None:
        f = tmp_path / "hostname"
        f.write_text("foo.onion.example.com\n")
        assert network_status.read_onion_address(f) is None


class TestGetTorAddressesExplicit:
    def test_reads_explicit_paths(self, tmp_path: Path) -> None:
        f = tmp_path / "hostname"
        f.write_text("explicit123.onion\n")
        assert network_status.get_tor_addresses([str(f)]) == ["explicit123.onion"]

    def test_deduplicates_addresses(self, tmp_path: Path) -> None:
        f = tmp_path / "hostname"
        f.write_text("same123.onion\n")
        addrs = network_status.get_tor_addresses([str(f), str(f)])
        assert addrs == ["same123.onion"]

    def test_explicit_paths_skip_auto_detect(self, tmp_path: Path) -> None:
        """When explicit paths are given, auto-detection must not run."""
        explicit = tmp_path / "explicit"
        explicit.write_text("explicit.onion\n")

        auto_root = tmp_path / "auto"
        auto_root.mkdir()
        (auto_root / "hostname").write_text("auto.onion\n")

        with patch.object(network_status, "TOR_SERVICE_DIRS", [str(auto_root)]):
            addrs = network_status.get_tor_addresses([str(explicit)])
        assert addrs == ["explicit.onion"]


class TestGetTorAddressesAutoDetect:
    def test_reads_hostname_directly_in_base_dir(self, tmp_path: Path) -> None:
        base = tmp_path / "tor"
        base.mkdir()
        (base / "hostname").write_text("direct.onion\n")

        with patch.object(network_status, "TOR_SERVICE_DIRS", [str(base)]):
            addrs = network_status.get_tor_addresses([])
        assert addrs == ["direct.onion"]

    def test_reads_hostname_from_subdirectory(self, tmp_path: Path) -> None:
        base = tmp_path / "onion-service"
        base.mkdir()
        svc = base / "clan_default"
        svc.mkdir()
        (svc / "hostname").write_text("sub.onion\n")

        with patch.object(network_status, "TOR_SERVICE_DIRS", [str(base)]):
            addrs = network_status.get_tor_addresses([])
        assert addrs == ["sub.onion"]

    def test_combines_direct_and_subdirectory_hostnames(self, tmp_path: Path) -> None:
        base = tmp_path / "tor"
        base.mkdir()
        (base / "hostname").write_text("top.onion\n")
        sub = base / "svc"
        sub.mkdir()
        (sub / "hostname").write_text("nested.onion\n")

        with patch.object(network_status, "TOR_SERVICE_DIRS", [str(base)]):
            addrs = network_status.get_tor_addresses([])
        # sorted alphabetically for stable auto-detect output
        assert addrs == ["nested.onion", "top.onion"]

    def test_auto_detected_sorted(self, tmp_path: Path) -> None:
        base = tmp_path / "tor"
        base.mkdir()
        for name, addr in [("z_svc", "zzz.onion"), ("a_svc", "aaa.onion")]:
            svc = base / name
            svc.mkdir()
            (svc / "hostname").write_text(f"{addr}\n")

        with patch.object(network_status, "TOR_SERVICE_DIRS", [str(base)]):
            addrs = network_status.get_tor_addresses([])
        assert addrs == ["aaa.onion", "zzz.onion"]

    def test_missing_base_dir_is_skipped(self, tmp_path: Path) -> None:
        missing = tmp_path / "does-not-exist"
        with patch.object(network_status, "TOR_SERVICE_DIRS", [str(missing)]):
            assert network_status.get_tor_addresses([]) == []
