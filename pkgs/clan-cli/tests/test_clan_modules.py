import pytest
from api import TestClient
from fixtures_flakes import FlakeForTest


@pytest.mark.with_core
def test_configure_machine(api: TestClient, test_flake_with_core: FlakeForTest) -> None:
    # retrieve the list of available clanModules
    response = api.get(f"/api/clan_modules?flake_dir={test_flake_with_core.path}")
    assert response.status_code == 200, response.text
    response_json = response.json()
    assert isinstance(response_json, dict)
    assert "clan_modules" in response_json
    assert len(response_json["clan_modules"]) > 0
    # ensure all entries are a string
    assert all(isinstance(x, str) for x in response_json["clan_modules"])
