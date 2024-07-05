import pytest
from helpers.cli import Cli


def test_help(capsys: pytest.CaptureFixture) -> None:
    cli = Cli()
    with pytest.raises(SystemExit):
        cli.run(["--help"])
    captured = capsys.readouterr()
    assert captured.out.startswith("usage:")
