import pytest
from helpers import cli


def test_help(capsys: pytest.CaptureFixture) -> None:
    with pytest.raises(SystemExit):
        cli.run(["--help"])
    captured = capsys.readouterr()
    assert captured.out.startswith("usage:")
