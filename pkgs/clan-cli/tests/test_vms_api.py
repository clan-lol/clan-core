from pathlib import Path

import pytest
from api import TestClient


@pytest.mark.impure
def test_inspect(api: TestClient, test_flake_with_core: Path) -> None:
    response = api.post(
        "/api/vms/inspect",
        json=dict(flake_url=str(test_flake_with_core), flake_attr="vm1"),
    )
    assert response.status_code == 200, "Failed to inspect vm"
    config = response.json()["config"]
    assert config.get("flake_attr") == "vm1"
    assert config.get("cores") == 1
    assert config.get("memory_size") == 1024
    assert config.get("graphics") is False


def test_incorrect_uuid(api: TestClient) -> None:
    uuid_endpoints = [
        "/api/vms/{}/status",
        "/api/vms/{}/logs",
    ]

    for endpoint in uuid_endpoints:
        response = api.get(endpoint.format("1234"))
        assert response.status_code == 422, "Failed to get vm status"
