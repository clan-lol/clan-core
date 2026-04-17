"""Tests for network_status.get_ip_addresses."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import network_status


def _run(stdout: str) -> MagicMock:
    result = MagicMock()
    result.stdout = stdout
    return result


class TestGetIpAddresses:
    def test_filters_loopback(self) -> None:
        mock = _run("lo UNKNOWN 127.0.0.1/8\neth0 UP 192.168.1.1/24")
        with patch("subprocess.run", return_value=mock):
            addrs = network_status.get_ip_addresses()
        assert len(addrs) == 1
        assert "192.168.1.1" in addrs[0]

    def test_filters_down_interfaces(self) -> None:
        mock = _run("eth0 DOWN 192.168.1.1/24\neth1 UP 10.0.0.1/24")
        with patch("subprocess.run", return_value=mock):
            addrs = network_status.get_ip_addresses()
        assert len(addrs) == 1
        assert "10.0.0.1" in addrs[0]

    def test_filters_link_local_ipv6(self) -> None:
        mock = _run("eth0 UP 192.168.1.1/24 fe80::1/64")
        with patch("subprocess.run", return_value=mock):
            addrs = network_status.get_ip_addresses()
        assert len(addrs) == 1
        assert "fe80" not in addrs[0]
        assert "192.168.1.1" in addrs[0]

    def test_interface_name_containing_up_substring_not_treated_as_up(self) -> None:
        """Regression: interface named 'UPLINK' must not bypass the state check."""
        mock = _run("UPLINK DOWN 192.168.1.1/24")
        with patch("subprocess.run", return_value=mock):
            addrs = network_status.get_ip_addresses()
        assert addrs == []

    def test_handles_empty_output(self) -> None:
        with patch("subprocess.run", return_value=_run("")):
            assert network_status.get_ip_addresses() == []

    def test_handles_multiple_up_interfaces(self) -> None:
        mock = _run("eth0 UP 192.168.1.1/24\nwlan0 UP 192.168.2.5/24")
        with patch("subprocess.run", return_value=mock):
            addrs = network_status.get_ip_addresses()
        assert len(addrs) == 2
        assert any("192.168.1.1" in a for a in addrs)
        assert any("192.168.2.5" in a for a in addrs)

    def test_returns_error_row_when_ip_command_missing(self) -> None:
        with patch("subprocess.run", side_effect=FileNotFoundError):
            addrs = network_status.get_ip_addresses()
        assert addrs == ["(ip command not found)"]

    def test_strips_ansi_color_codes_for_state_parsing(self) -> None:
        """Real `ip -color addr` emits ANSI SGR codes around the state field."""
        colored = "eth0 \x1b[01;32mUP\x1b[0m 192.168.1.1/24"
        with patch("subprocess.run", return_value=_run(colored)):
            addrs = network_status.get_ip_addresses()
        assert len(addrs) == 1
        assert "192.168.1.1" in addrs[0]

    def test_name_with_parent_link_suffix_is_kept(self) -> None:
        """iproute2 emits `name@parent` for veth/macvlan/WireGuard (`wg0@NONE`).

        The `@parent` suffix must not trip the iface==lo check.
        """
        mock = _run("veth0@if7 UP 10.0.0.1/24")
        with patch("subprocess.run", return_value=mock):
            addrs = network_status.get_ip_addresses()
        assert len(addrs) == 1
        assert "veth0@if7" in addrs[0]
        assert "10.0.0.1" in addrs[0]

    def test_multiple_addresses_mixed_families(self) -> None:
        """A single interface with v4, routable v6 and fe80:: all on one brief line."""
        mock = _run("eth0 UP 192.168.1.1/24 2001:db8::1/64 fe80::1/64")
        with patch("subprocess.run", return_value=mock):
            addrs = network_status.get_ip_addresses()
        assert len(addrs) == 1
        assert "192.168.1.1/24" in addrs[0]
        assert "2001:db8::1/64" in addrs[0]
        assert "fe80" not in addrs[0]

    def test_non_up_states_filtered(self) -> None:
        """DORMANT, LOWERLAYERDOWN, NOTPRESENT, TESTING are all non-UP."""
        for state in ("DORMANT", "LOWERLAYERDOWN", "NOTPRESENT", "TESTING"):
            mock = _run(f"eth0 {state} 192.168.1.1/24")
            with patch("subprocess.run", return_value=mock):
                assert network_status.get_ip_addresses() == []
