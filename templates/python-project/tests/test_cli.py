import sys

import my_tool


def test_no_args(capsys):
    my_tool.my_cli()
    captured = capsys.readouterr()
    assert captured.out.startswith("usage:")


def test_version(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["", "--version"])
    my_tool.my_cli()
    captured = capsys.readouterr()
    assert captured.out.startswith("Version:")
