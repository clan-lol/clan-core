import json
import logging
from pathlib import Path

import pytest
from api import TestClient
from fixtures_flakes import FlakeForTest

from clan_cli.flakes.create import DEFAULT_URL

log = logging.getLogger(__name__)


@pytest.mark.impure
def test_flake_create(api: TestClient, temporary_home: Path) -> None:
    params = {"flake_name": "defaultFlake", "url": str(DEFAULT_URL)}
    response = api.post(
        "/api/flake/create",
        json=params,
    )

    response.json()
    assert response.status_code == 201, "Failed to create flake"


# @pytest.mark.impure
# def test_flake_create_fail(api: TestClient, temporary_home: Path) -> None:
#     params = {
#         "flake_name": "../../../defaultFlake/",
#         "url": str(DEFAULT_URL)
#     }
#     response = api.post(
#         "/api/flake/create",
#         json=params,
#     )

#     data = response.json()
#     log.debug("Data: %s", data)
#     assert response.status_code == 422, "This should have failed"


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
