import sys

import pytest

import my_tool


def test_no_args(capsys: pytest.CaptureFixture) -> None:
    my_tool.my_cli()
    captured = capsys.readouterr()
    assert captured.out.startswith("usage:")


def test_version(
    capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(sys, "argv", ["", "--version"])
    my_tool.my_cli()
    captured = capsys.readouterr()
    assert captured.out.startswith("Version:")
