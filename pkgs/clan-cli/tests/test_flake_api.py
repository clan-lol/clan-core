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
