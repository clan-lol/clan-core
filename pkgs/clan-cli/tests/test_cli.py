import sys

import pytest

import clan


def test_no_args(capsys):
    clan.clan()
    captured = capsys.readouterr()
    assert captured.out.startswith("usage:")


def test_help(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["", "--help"])
    with pytest.raises(SystemExit):
        clan.clan()
    captured = capsys.readouterr()
    assert captured.out.startswith("usage:")
