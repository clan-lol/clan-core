from typing import TYPE_CHECKING

import pytest
from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_lib.flake import Flake
from clan_lib.services.modules import list_service_modules

if TYPE_CHECKING:
    pass


@pytest.mark.with_core
def test_list_modules(test_flake_with_core: FlakeForTest) -> None:
    base_path = test_flake_with_core.path
    modules_info = list_service_modules(Flake(str(base_path)))

    assert "modules" in modules_info
