from pathlib import Path

from api import TestClient


def test_machines(api: TestClient, clan_flake: Path) -> None:
    response = api.get("/api/machines")
    assert response.status_code == 200
    assert response.json() == {"machines": []}

    response = api.post("/api/machines", json={"name": "test"})
    assert response.status_code == 201
    assert response.json() == {"machine": {"name": "test", "status": "unknown"}}

    response = api.get("/api/machines/test")
    assert response.status_code == 200
    assert response.json() == {"machine": {"name": "test", "status": "unknown"}}

    response = api.get("/api/machines")
    assert response.status_code == 200
    assert response.json() == {"machines": [{"name": "test", "status": "unknown"}]}


def test_configure_machine(api: TestClient, machine_flake: Path) -> None:
    response = api.get("/api/machines/machine1/config")
    assert response.status_code == 200
    assert response.json() == {"config": dict()}

    # set some config
    response = api.put(
        "/api/machines/machine1/config",
        json=dict(
            clan=dict(
                jitsi=True,
            )
        ),
    )
    assert response.status_code == 200
    assert response.json() == {"config": {"clan": {"jitsi": True}}}

    # get the config again
    response = api.get("/api/machines/machine1/config")
    assert response.status_code == 200
    assert response.json() == {"config": {"clan": {"jitsi": True}}}
