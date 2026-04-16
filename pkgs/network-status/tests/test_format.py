"""Tests for formatting helpers: center_text and get_terminal_width."""

from __future__ import annotations

from os import terminal_size
from unittest.mock import patch

import network_status


class TestCenterText:
    def test_centers_single_line(self) -> None:
        result = network_status.center_text("hello", 20)
        # (20-5)//2 = 7 spaces padding
        assert result == "       hello"

    def test_centers_multiple_lines(self) -> None:
        result = network_status.center_text("ab\ncd", 10)
        lines = result.splitlines()
        assert lines == ["    ab", "    cd"]

    def test_handles_empty_string(self) -> None:
        assert network_status.center_text("", 20) == ""

    def test_handles_line_wider_than_width(self) -> None:
        result = network_status.center_text("very long line", 5)
        assert result == "very long line"

    def test_uses_longest_line_for_padding(self) -> None:
        """All lines share the padding derived from the longest line."""
        result = network_status.center_text("ab\nabcdef", 20)
        lines = result.splitlines()
        # longest line is 6 chars → (20-6)//2 = 7 padding for every line
        assert lines == ["       ab", "       abcdef"]


class TestGetTerminalWidth:
    def test_returns_default_on_failure(self) -> None:
        with patch("shutil.get_terminal_size", side_effect=OSError):
            assert network_status.get_terminal_width() == 80

    def test_returns_actual_columns(self) -> None:
        fake = terminal_size((123, 42))
        with patch("shutil.get_terminal_size", return_value=fake):
            assert network_status.get_terminal_width() == 123
