import os
from pathlib import Path

import pytest
from api import TestClient
from httpx import SyncByteStream


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


@pytest.mark.skipif(not os.path.exists("/dev/kvm"), reason="Requires KVM")
@pytest.mark.impure
def test_create(api: TestClient, test_flake_with_core: Path) -> None:
    print(f"flake_url: {test_flake_with_core} ")
    response = api.post(
        "/api/vms/create",
        json=dict(
            flake_url=str(test_flake_with_core),
            flake_attr="vm1",
            cores=1,
            memory_size=1024,
            graphics=False,
        ),
    )
    assert response.status_code == 200, "Failed to create vm"

    uuid = response.json()["uuid"]
    assert len(uuid) == 36
    assert uuid.count("-") == 4

    response = api.get(f"/api/vms/{uuid}/status")
    assert response.status_code == 200, "Failed to get vm status"

    response = api.get(f"/api/vms/{uuid}/logs")
    print("=========VM LOGS==========")
    assert isinstance(response.stream, SyncByteStream)
    for line in response.stream:
        assert line != b"", "Failed to get vm logs"
        print(line.decode("utf-8"))
    print("=========END LOGS==========")
    assert response.status_code == 200, "Failed to get vm logs"

    response = api.get(f"/api/vms/{uuid}/status")
    assert response.status_code == 200, "Failed to get vm status"
    returncodes = response.json()["returncode"]
    assert response.json()["running"] is False, "VM is still running. Should be stopped"
    for exit_code in returncodes:
        assert exit_code == 0, "One VM failed with exit code != 0"
