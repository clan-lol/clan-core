import pytest
from helpers.cli import Cli


def test_help(capfd: pytest.CaptureFixture) -> None:
    cli = Cli()
    with pytest.raises(SystemExit):
        cli.run(["clan-app", "--help"])
