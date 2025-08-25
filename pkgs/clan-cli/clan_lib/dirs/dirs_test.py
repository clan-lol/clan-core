from collections.abc import Callable
from pathlib import Path

import pytest
from clan_cli.tests.fixtures_flakes import FlakeForTest

from clan_lib.dirs import clan_key_safe, get_clan_directories, vm_state_dir
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
""",
    )

    test_subdir = Path(flake.path) / "direct-config"
    test_subdir.mkdir(exist_ok=True)

    source_dir, computed_dir = get_clan_directories(flake)

    assert source_dir.startswith("/nix/store/")
    assert "source" in source_dir

    assert computed_dir == "direct-config"


def test_clan_key_safe() -> None:
    assert clan_key_safe("/foo/bar") == "%2Ffoo%2Fbar"


def test_vm_state_dir_identity() -> None:
    dir1 = vm_state_dir("https://some.clan", "vm1")
    dir2 = vm_state_dir("https://some.clan", "vm1")
    assert str(dir1) == str(dir2)


def test_vm_state_dir_no_collision() -> None:
    dir1 = vm_state_dir("/foo/bar", "vm1")
    dir2 = vm_state_dir("https://some.clan", "vm1")
    assert str(dir1) != str(dir2)
