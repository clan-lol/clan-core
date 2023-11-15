import pytest
from cli import Cli
from fixtures_flakes import FlakeForTest


def test_machine_subcommands(
    test_flake: FlakeForTest, capsys: pytest.CaptureFixture
) -> None:
    cli = Cli()
    cli.run(["--flake", str(test_flake.path), "machines", "create", "machine1"])

    capsys.readouterr()
    cli.run(["--flake", str(test_flake.path), "machines", "list"])
    out = capsys.readouterr()
    assert "machine1\n" == out.out

    cli.run(["--flake", str(test_flake.path), "machines", "delete", "machine1"])

    capsys.readouterr()
    cli.run(["--flake", str(test_flake.path), "machines", "list"])
    out = capsys.readouterr()
    assert "" == out.out
