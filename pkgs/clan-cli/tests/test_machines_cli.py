from pathlib import Path

import pytest
from cli import Cli
from fixtures_flakes import FlakeForTest

def test_machine_subcommands(test_flake: FlakeForTest, capsys: pytest.CaptureFixture) -> None:
    cli = Cli()
    cli.run(["machines", "create", "machine1", test_flake.name])

    capsys.readouterr()
    cli.run(["machines", "list", test_flake.name])
    out = capsys.readouterr()
    assert "machine1\n" == out.out

    cli.run(["machines", "delete", "machine1", test_flake.name])

    capsys.readouterr()
    cli.run(["machines", "list", test_flake.name])
    out = capsys.readouterr()
    assert "" == out.out
