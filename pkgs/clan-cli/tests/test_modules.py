import pytest
from fixtures_flakes import FlakeForTest

from clan_cli.api.modules import list_modules, show_module_info


@pytest.mark.with_core
def test_list_modules(test_flake_with_core: FlakeForTest) -> None:
    base_path = test_flake_with_core.path
    module_list = list_modules(base_path)
    assert isinstance(module_list, list)
    assert len(module_list) > 1
    # Random test for those two modules
    assert "borgbackup" in module_list
    assert "syncthing" in module_list


@pytest.mark.with_core
def test_modules_details(test_flake_with_core: FlakeForTest) -> None:
    base_path = test_flake_with_core.path
    test_module = "borgbackup"
    module_info = show_module_info(base_path, test_module)
    assert module_info.description is not None and module_info.description != ""
    assert module_info.categories and "backup" in module_info.categories
    assert module_info.roles
    assert set(module_info.roles) == {"server", "client"}
