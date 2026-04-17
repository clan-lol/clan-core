"""Tests for print_status output layout."""

from __future__ import annotations

from typing import TYPE_CHECKING

import network_status

if TYPE_CHECKING:
    import pytest


class TestPrintStatus:
    def test_output_contains_all_sections(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        network_status.print_status(
            ip_addrs=["eth0 UP 192.168.1.1/24"],
            vpn_addrs=["wg0 UP 10.0.0.1/24"],
            tor_addrs=["test123.onion"],
            hostname="testhost",
        )
        out = capsys.readouterr().out
        assert "Network Information" in out
        assert "192.168.1.1" in out
        assert "VPN Networks" in out
        assert "10.0.0.1" in out
        assert "Tor Hidden Services" in out
        assert "test123.onion" in out
        assert "Multicast DNS" in out
        assert "testhost.local" in out

    def test_hides_vpn_section_when_empty(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        network_status.print_status(
            ip_addrs=["eth0 UP 192.168.1.1/24"],
            vpn_addrs=[],
            tor_addrs=[],
            hostname="testhost",
        )
        out = capsys.readouterr().out
        assert "Network Information" in out
        assert "VPN Networks" not in out
        assert "Tor Hidden Services" not in out

    def test_shows_tor_without_vpn(self, capsys: pytest.CaptureFixture[str]) -> None:
        network_status.print_status(
            ip_addrs=["eth0 UP 192.168.1.1/24"],
            vpn_addrs=[],
            tor_addrs=["only.onion"],
            hostname="testhost",
        )
        out = capsys.readouterr().out
        assert "VPN Networks" not in out
        assert "Tor Hidden Services" in out
        assert "only.onion" in out

    def test_all_optional_sections_empty(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        network_status.print_status(
            ip_addrs=[],
            vpn_addrs=[],
            tor_addrs=[],
            hostname="testhost",
        )
        out = capsys.readouterr().out
        assert "Network Information" in out
        assert "VPN Networks" not in out
        assert "Tor Hidden Services" not in out
        assert "testhost.local" in out

    def test_footer_present(self, capsys: pytest.CaptureFixture[str]) -> None:
        network_status.print_status(
            ip_addrs=["eth0 UP 192.168.1.1/24"],
            vpn_addrs=[],
            tor_addrs=[],
            hostname="testhost",
        )
        assert "Ctrl-C" in capsys.readouterr().out
