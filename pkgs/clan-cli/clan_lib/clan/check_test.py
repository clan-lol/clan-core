from pathlib import Path

from clan_cli.tests.fixtures_flakes import FlakeForTest

from clan_lib.clan.check import check_clan_valid
from clan_lib.flake import Flake


def test_check_clan_valid(
    temporary_home: Path, test_flake_with_core: FlakeForTest, test_flake: FlakeForTest
) -> None:
    # Test with a valid clan
    flake = Flake(str(test_flake_with_core.path))
    assert check_clan_valid(flake) is True

    # Test with an invalid clan
    flake = Flake(str(test_flake.path))
    assert check_clan_valid(flake) is False

    # Test with a non-existent clan
    flake = Flake(str(temporary_home))
    assert check_clan_valid(flake) is False
