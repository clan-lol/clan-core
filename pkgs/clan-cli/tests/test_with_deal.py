import deal

from clan_cli import nix


@deal.cases(nix.nix_shell)
def test_nix_shell(case: deal.TestCase) -> None:
    case()
