import pytest
from helpers import cli


def test_help() -> None:
    with pytest.raises(SystemExit):
        cli.run(["clan-app", "--help"])
