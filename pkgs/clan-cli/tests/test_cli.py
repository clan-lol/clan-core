import sys

import clan_cli
import pytest


def test_no_args(capsys):
    clan_cli.main()
    captured = capsys.readouterr()
    assert captured.out.startswith("usage:")


def test_help(capsys: pytest.CaptureFixture, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["", "--help"])
    with pytest.raises(SystemExit):
        clan_cli.main()
    captured = capsys.readouterr()
    assert captured.out.startswith("usage:")
