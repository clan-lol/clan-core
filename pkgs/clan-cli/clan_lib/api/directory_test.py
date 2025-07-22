from collections.abc import Callable
from pathlib import Path

import pytest
from clan_cli.tests.fixtures_flakes import FlakeForTest

from clan_lib.api.directory import get_clan_directories
from clan_lib.errors import ClanError
from clan_lib.flake import Flake


@pytest.mark.with_core
def test_get_clan_directories_default(test_flake_with_core: FlakeForTest) -> None:
    flake = Flake(str(test_flake_with_core.path))
    source_dir, computed_dir = get_clan_directories(flake)

    assert source_dir.startswith("/nix/store/")
    assert "source" in source_dir

    computed_path = Path(computed_dir)

    assert computed_path == Path()


@pytest.mark.with_core
def test_get_clan_directories_invalid_flake() -> None:
    invalid_flake = Flake("/non/existent/path")

    with pytest.raises(ClanError):
        get_clan_directories(invalid_flake)


@pytest.mark.with_core
def test_get_clan_directories_with_direct_directory_config(
    clan_flake: Callable[..., Flake],
) -> None:
    """Test get_clan_directories with clan.directory set directly in Nix configuration"""
    flake = clan_flake(
        raw="""
{
  directory = ./direct-config;
}
"""
    )

    test_subdir = Path(flake.path) / "direct-config"
    test_subdir.mkdir(exist_ok=True)

    source_dir, computed_dir = get_clan_directories(flake)

    assert source_dir.startswith("/nix/store/")
    assert "source" in source_dir

    assert computed_dir == "direct-config"
