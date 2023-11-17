import json
import logging

import pytest
from api import TestClient
from fixtures_flakes import FlakeForTest
from path import Path

from clan_cli.dirs import user_history_file

log = logging.getLogger(__name__)


def test_flake_add(
    api: TestClient, test_flake: FlakeForTest, temporary_home: Path
) -> None:
    response = api.put(
        f"/api/flake/add?flake_dir={str(test_flake.path)}",
        json={},
    )
    assert response.status_code == 200, response.json()
    assert user_history_file().exists()
    assert open(user_history_file()).read().strip() == str(test_flake.path)


@pytest.mark.impure
def test_inspect_ok(api: TestClient, test_flake_with_core: FlakeForTest) -> None:
    params = {"url": str(test_flake_with_core.path)}
    response = api.get(
        "/api/flake/attrs",
        params=params,
    )
    assert response.status_code == 200, "Failed to inspect vm"
    data = response.json()
    print("Data: ", data)
    assert data.get("flake_attrs") == ["vm1", "vm2"]


@pytest.mark.impure
def test_inspect_err(api: TestClient) -> None:
    params = {"url": "flake-parts"}
    response = api.get(
        "/api/flake/attrs",
        params=params,
    )
    assert response.status_code != 200, "Succeed to inspect vm but expected to fail"
    data = response.json()
    print("Data: ", data)
    assert data.get("detail")


@pytest.mark.impure
def test_inspect_flake(api: TestClient, test_flake_with_core: FlakeForTest) -> None:
    params = {"url": str(test_flake_with_core.path)}
    response = api.get(
        "/api/flake/inspect",
        params=params,
    )
    assert response.status_code == 200, "Failed to inspect vm"
    data = response.json()
    print("Data: ", json.dumps(data, indent=2))
    assert data.get("content") is not None
    actions = data.get("actions")
    assert actions is not None
    assert len(actions) == 2
    assert actions[0].get("id") == "vms/inspect"
    assert actions[0].get("uri") == "api/vms/inspect"
    assert actions[1].get("id") == "vms/create"
    assert actions[1].get("uri") == "api/vms/create"
