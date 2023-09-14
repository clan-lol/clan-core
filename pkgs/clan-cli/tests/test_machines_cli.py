from pathlib import Path

import pytest
from cli import Cli


def test_machine_subcommands(clan_flake: Path, capsys: pytest.CaptureFixture) -> None:
    cli = Cli()
    cli.run(["machines", "create", "machine1"])

    capsys.readouterr()
    cli.run(["machines", "list"])
    out = capsys.readouterr()
    assert "machine1\n" == out.out

    cli.run(["machines", "remove", "machine1"])

    capsys.readouterr()
    cli.run(["machines", "list"])
    out = capsys.readouterr()
    assert "" == out.out
