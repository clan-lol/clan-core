"""Tests for network_status.get_hostname."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import network_status


class TestGetHostname:
    def test_returns_nixos_when_file_not_found(self) -> None:
        with patch.object(Path, "read_text", side_effect=FileNotFoundError):
            assert network_status.get_hostname() == "nixos"

    def test_returns_nixos_on_permission_error(self) -> None:
        with patch.object(Path, "read_text", side_effect=PermissionError):
            assert network_status.get_hostname() == "nixos"

    def test_returns_nixos_when_path_is_directory(self) -> None:
        with patch.object(Path, "read_text", side_effect=IsADirectoryError):
            assert network_status.get_hostname() == "nixos"

    def test_returns_nixos_on_binary_content(self) -> None:
        err = UnicodeDecodeError("utf-8", b"\xff\xfe", 0, 1, "invalid start byte")
        with patch.object(Path, "read_text", side_effect=err):
            assert network_status.get_hostname() == "nixos"

    def test_returns_hostname_from_file(self) -> None:
        with patch.object(Path, "read_text", return_value="myhost\n"):
            assert network_status.get_hostname() == "myhost"

    def test_strips_whitespace(self) -> None:
        with patch.object(Path, "read_text", return_value="  testhost  \n"):
            assert network_status.get_hostname() == "testhost"
