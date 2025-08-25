import pytest
from cli import Cli


def test_help() -> None:
    cli = Cli()
    with pytest.raises(SystemExit):
        cli.run(["clan-vm-manager", "--help"])
