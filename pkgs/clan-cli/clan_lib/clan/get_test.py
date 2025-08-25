import pytest
from clan_cli.tests.fixtures_flakes import FlakeForTest

from clan_lib.clan.get import get_clan_details
from clan_lib.flake import Flake, FlakeDoesNotExistError, FlakeInvalidError


@pytest.mark.with_core
def test_get_clan_details_invalid_flake() -> None:
    invalid_flake = Flake("/non/existent/path")

    with pytest.raises(FlakeDoesNotExistError):
        get_clan_details(invalid_flake)

    with pytest.raises(FlakeInvalidError):
        get_clan_details(Flake("/tmp"))  # noqa: S108


@pytest.mark.with_core
def test_get_clan_details(test_flake_with_core: FlakeForTest) -> None:
    flake = Flake(str(test_flake_with_core.path))
    details = get_clan_details(flake)

    assert details["name"] == "test_flake_with_core"
