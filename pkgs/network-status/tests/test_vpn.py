"""Tests for VPN interface detection and address retrieval."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import network_status


def _run(stdout: str) -> MagicMock:
    result = MagicMock()
    result.stdout = stdout
    return result


def _fake_iface(name: str) -> MagicMock:
    iface = MagicMock()
    iface.name = name
    return iface


class TestDetectVpnInterfaces:
    def test_detects_wireguard_interfaces(self) -> None:
        mock = _run("3: wg0: <POINTOPOINT,NOARP,UP> mtu 1420")
        with (
            patch("subprocess.run", return_value=mock),
            patch.object(Path, "exists", return_value=False),
        ):
            assert "wg0" in network_status.detect_vpn_interfaces()

    def test_detects_wireguard_with_carrier_suffix(self) -> None:
        mock = _run("5: wg0@carrier0: <POINTOPOINT,NOARP,UP> mtu 1420")
        with (
            patch("subprocess.run", return_value=mock),
            patch.object(Path, "exists", return_value=False),
        ):
            interfaces = network_status.detect_vpn_interfaces()
        assert "wg0" in interfaces
        assert "wg0@carrier0" not in interfaces

    def test_detects_zerotier_interfaces(self) -> None:
        with (
            patch("subprocess.run", return_value=_run("")),
            patch.object(Path, "exists", return_value=True),
            patch.object(
                Path,
                "iterdir",
                return_value=[_fake_iface("eth0"), _fake_iface("zt1234abc")],
            ),
        ):
            interfaces = network_status.detect_vpn_interfaces()
        assert "zt1234abc" in interfaces
        assert "eth0" not in interfaces

    def test_detects_yggdrasil_interfaces(self) -> None:
        with (
            patch("subprocess.run", return_value=_run("")),
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "iterdir", return_value=[_fake_iface("ygg")]),
        ):
            assert "ygg" in network_status.detect_vpn_interfaces()

    def test_detects_tailscale_interfaces(self) -> None:
        with (
            patch("subprocess.run", return_value=_run("")),
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "iterdir", return_value=[_fake_iface("tailscale0")]),
        ):
            assert "tailscale0" in network_status.detect_vpn_interfaces()

    def test_detects_mycelium_interfaces(self) -> None:
        with (
            patch("subprocess.run", return_value=_run("")),
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "iterdir", return_value=[_fake_iface("mycelium0")]),
        ):
            assert "mycelium0" in network_status.detect_vpn_interfaces()

    def test_dedup_when_wireguard_matches_name_pattern(self) -> None:
        """If the same iface is detected by both methods, keep only one."""
        mock = _run("3: ztwg: <POINTOPOINT,NOARP,UP> mtu 1420")
        with (
            patch("subprocess.run", return_value=mock),
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "iterdir", return_value=[_fake_iface("ztwg")]),
        ):
            interfaces = network_status.detect_vpn_interfaces()
        assert interfaces.count("ztwg") == 1

    def test_ip_command_missing_falls_back_to_sysfs(self) -> None:
        with (
            patch("subprocess.run", side_effect=FileNotFoundError),
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "iterdir", return_value=[_fake_iface("ygg")]),
        ):
            assert network_status.detect_vpn_interfaces() == ["ygg"]

    def test_detects_multiple_wireguard_interfaces(self) -> None:
        """`ip link show type wireguard` lists each interface on its own stanza."""
        output = (
            "3: wg0: <POINTOPOINT,NOARP,UP> mtu 1420 qdisc noqueue state UNKNOWN\n"
            "    link/none\n"
            "4: wg1: <POINTOPOINT,NOARP,UP> mtu 1420 qdisc noqueue state UNKNOWN\n"
            "    link/none"
        )
        with (
            patch("subprocess.run", return_value=_run(output)),
            patch.object(Path, "exists", return_value=False),
        ):
            interfaces = network_status.detect_vpn_interfaces()
        assert interfaces == ["wg0", "wg1"]

    def test_ignores_link_ether_continuation(self) -> None:
        """The `link/ether <mac>` continuation contains colons but no `": "`.

        Ensure we don't parse the MAC address as an interface name.
        """
        output = (
            "2: eth0: <BROADCAST,MULTICAST,UP> mtu 1500 qdisc fq_codel state UP\n"
            "    link/ether 00:11:22:33:44:55 brd ff:ff:ff:ff:ff:ff"
        )
        with (
            patch("subprocess.run", return_value=_run(output)),
            patch.object(Path, "exists", return_value=False),
        ):
            interfaces = network_status.detect_vpn_interfaces()
        assert "00" not in interfaces
        assert "eth0" in interfaces


class TestGetVpnAddresses:
    def test_returns_addresses_for_up_interface(self) -> None:
        with patch("subprocess.run", return_value=_run("wg0 UP 10.0.0.1/24")):
            addrs = network_status.get_vpn_addresses(["wg0"])
        assert len(addrs) == 1
        assert "10.0.0.1" in addrs[0]

    def test_handles_unknown_state(self) -> None:
        """UNKNOWN is common for virtual interfaces like ZeroTier."""
        mock = _run("zt0 UNKNOWN fdd7:10e7:a9c5::1/88")
        with patch("subprocess.run", return_value=mock):
            addrs = network_status.get_vpn_addresses(["zt0"])
        assert len(addrs) == 1
        assert "fdd7:10e7" in addrs[0]
        assert "OFFLINE" not in addrs[0]

    def test_shows_offline_for_down_interface(self) -> None:
        with patch("subprocess.run", return_value=_run("wg0 DOWN")):
            addrs = network_status.get_vpn_addresses(["wg0"])
        assert addrs == ["wg0 OFFLINE"]

    def test_shows_offline_for_empty_output(self) -> None:
        with patch("subprocess.run", return_value=_run("")):
            addrs = network_status.get_vpn_addresses(["wg0"])
        assert addrs == ["wg0 OFFLINE"]

    def test_shows_no_addresses_when_only_link_local(self) -> None:
        with patch("subprocess.run", return_value=_run("zt0 UNKNOWN fe80::1234/64")):
            addrs = network_status.get_vpn_addresses(["zt0"])
        assert addrs == ["zt0 UP (no addresses)"]

    def test_mixed_fe80_and_routable_keeps_routable(self) -> None:
        mock = _run("wg0 UP 10.0.0.1/24 fe80::1/64")
        with patch("subprocess.run", return_value=mock):
            addrs = network_status.get_vpn_addresses(["wg0"])
        assert len(addrs) == 1
        assert "10.0.0.1" in addrs[0]
        assert "fe80" not in addrs[0]

    def test_multiple_interfaces_returned_in_order(self) -> None:
        side_effects = [_run("wg0 UP 10.0.0.1/24"), _run("zt0 DOWN")]
        with patch("subprocess.run", side_effect=side_effects):
            addrs = network_status.get_vpn_addresses(["wg0", "zt0"])
        assert len(addrs) == 2
        assert "10.0.0.1" in addrs[0]
        assert "OFFLINE" in addrs[1]

    def test_ip_command_missing_reports_per_interface(self) -> None:
        with patch("subprocess.run", side_effect=FileNotFoundError):
            addrs = network_status.get_vpn_addresses(["wg0"])
        assert addrs == ["wg0 (ip command not found)"]

    def test_name_with_none_parent_suffix_accepted(self) -> None:
        """iproute2 emits `wg0@NONE` in brief addr output for linkless WG.

        The first field isn't the user-facing iface name we requested — it
        comes from netlink. We must accept it and still surface the address.
        """
        mock = _run("wg0@NONE UNKNOWN 10.100.0.1/32")
        with patch("subprocess.run", return_value=mock):
            addrs = network_status.get_vpn_addresses(["wg0"])
        assert len(addrs) == 1
        assert "10.100.0.1" in addrs[0]
        assert "OFFLINE" not in addrs[0]

    def test_mixed_v4_and_v6_routable_with_link_local(self) -> None:
        """Keep both v4 and v6 routable addresses, drop fe80:: link-local."""
        mock = _run("wg0 UP 10.0.0.1/24 fdd7:10e7:a9c5::1/64 fe80::abcd/64")
        with patch("subprocess.run", return_value=mock):
            addrs = network_status.get_vpn_addresses(["wg0"])
        assert len(addrs) == 1
        assert "10.0.0.1/24" in addrs[0]
        assert "fdd7:10e7:a9c5::1/64" in addrs[0]
        assert "fe80" not in addrs[0]
