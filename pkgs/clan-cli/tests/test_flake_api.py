import json
from pathlib import Path

import pytest
from api import TestClient


@pytest.mark.impure
def test_inspect_ok(api: TestClient, test_flake_with_core: Path) -> None:
    params = {"url": str(test_flake_with_core)}
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
def test_inspect_flake(api: TestClient, test_flake_with_core: Path) -> None:
    params = {"url": str(test_flake_with_core)}
    response = api.get(
        "/api/flake",
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
