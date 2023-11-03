import json
import logging

import pytest
from api import TestClient
from fixtures_flakes import FlakeForTest

log = logging.getLogger(__name__)

@pytest.mark.impure
def test_list_flakes(api: TestClient, test_flake_with_core: FlakeForTest) -> None:
    response = api.get("/api/flake/list")
    assert response.status_code == 200, "Failed to list flakes"
    data = response.json()
    print("Data: ", data)
    assert data.get("flakes") == ["test_flake_with_core"]


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
    assert data.get("flake_attrs") == ["vm1"]


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
