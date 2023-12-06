import deal

from clan_cli import nix


@deal.cases(nix.nix_command)
def test_nix_command(case: deal.TestCase) -> None:
    case()


@deal.cases(nix.nix_build)
def test_nix_build(case: deal.TestCase) -> None:
    case()


@deal.cases(nix.nix_config)
def test_nix_config(case: deal.TestCase) -> None:
    case()


@deal.cases(nix.nix_eval)
def test_nix_eval(case: deal.TestCase) -> None:
    case()


@deal.cases(nix.nix_shell)
def test_nix_shell(case: deal.TestCase) -> None:
    case()
