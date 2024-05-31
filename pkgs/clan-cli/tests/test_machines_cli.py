import pytest
from cli import Cli
from fixtures_flakes import FlakeForTest


@pytest.mark.impure
def test_machine_subcommands(
    test_flake_with_core: FlakeForTest, capsys: pytest.CaptureFixture
) -> None:
    cli = Cli()
    cli.run(
        ["machines", "create", "--flake", str(test_flake_with_core.path), "machine1"]
    )

    capsys.readouterr()
    cli.run(["machines", "list", "--flake", str(test_flake_with_core.path)])

    out = capsys.readouterr()

    assert "machine1" in out.out
    assert "vm1" in out.out
    assert "vm2" in out.out

    capsys.readouterr()
    cli.run(["machines", "show", "--flake", str(test_flake_with_core.path), "machine1"])
    out = capsys.readouterr()
    assert "machine1" in out.out
    assert "Description" in out.out
    print(out)

    cli.run(
        ["machines", "delete", "--flake", str(test_flake_with_core.path), "machine1"]
    )

    capsys.readouterr()
    cli.run(["machines", "list", "--flake", str(test_flake_with_core.path)])
    out = capsys.readouterr()

    assert "machine1" not in out.out
    assert "vm1" in out.out
    assert "vm2" in out.out
