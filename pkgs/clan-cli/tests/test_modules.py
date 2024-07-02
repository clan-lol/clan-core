import pytest
from fixtures_flakes import FlakeForTest

from clan_cli.api.modules import list_modules


@pytest.mark.with_core
def test_list_modules(test_flake_with_core: FlakeForTest) -> None:
    base_path = test_flake_with_core.path
    modules_info = list_modules(base_path)

    assert len(modules_info.items()) > 1
    # Random test for those two modules
    assert "borgbackup" in modules_info.keys()
    assert "syncthing" in modules_info.keys()
