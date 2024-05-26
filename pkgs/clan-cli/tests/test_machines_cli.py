import pytest
from cli import Cli
from fixtures_flakes import FlakeForTest


@pytest.mark.impure
def test_machine_subcommands(
    test_flake_with_core: FlakeForTest, capsys: pytest.CaptureFixture
) -> None:
    cli = Cli()
    cli.run(
        ["--flake", str(test_flake_with_core.path), "machines", "create", "machine1"]
    )

    capsys.readouterr()
    cli.run(["--flake", str(test_flake_with_core.path), "machines", "list"])

    out = capsys.readouterr()

    assert "machine1" in out.out
    assert "nvm1" in out.out
    assert "nvm2" in out.out

    cli.run(
        ["--flake", str(test_flake_with_core.path), "machines", "delete", "machine1"]
    )

    capsys.readouterr()
    cli.run(["--flake", str(test_flake_with_core.path), "machines", "list"])
    out = capsys.readouterr()

    assert "machine1" not in out.out
    assert "nvm1" in out.out
    assert "nvm2" in out.out
