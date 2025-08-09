from collections.abc import Callable
from pathlib import Path

import pytest
from clan_cli.tests.fixtures_flakes import FlakeForTest

from clan_lib.api.directory import get_clan_directory_relative
from clan_lib.errors import ClanError
from clan_lib.flake import Flake


@pytest.mark.with_core
def test_get_relative_clan_directory_default(
    test_flake_with_core: FlakeForTest,
) -> None:
    flake = Flake(str(test_flake_with_core.path))
    relative_dir = get_clan_directory_relative(flake)

    # Default configuration should return ""
    assert relative_dir == ""


@pytest.mark.with_core
def test_get_relative_clan_directory_custom(
    clan_flake: Callable[..., Flake],
) -> None:
    flake = clan_flake(
        raw="""
{
  directory = ./direct-config;
}
"""
    )

    test_subdir = Path(flake.path) / "direct-config"
    test_subdir.mkdir(exist_ok=True)

    relative_dir = get_clan_directory_relative(flake)

    assert relative_dir == "direct-config"


@pytest.mark.with_core
def test_get_relative_clan_directory_invalid_flake() -> None:
    invalid_flake = Flake("/non/existent/path")

    with pytest.raises(ClanError):
        get_clan_directory_relative(invalid_flake)
