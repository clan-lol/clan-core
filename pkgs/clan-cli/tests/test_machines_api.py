from pathlib import Path

from api import TestClient


def test_machines(api: TestClient, test_flake: Path) -> None:
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


def test_configure_machine(api: TestClient, test_flake: Path) -> None:
    # ensure error 404 if machine does not exist when accessing the config
    response = api.get("/api/machines/machine1/config")
    assert response.status_code == 404

    # ensure error 404 if machine does not exist when writing to the config
    response = api.put("/api/machines/machine1/config", json={})
    assert response.status_code == 404

    # create the machine
    response = api.post("/api/machines", json={"name": "machine1"})
    assert response.status_code == 201

    # ensure an empty config is returned by default for a new machine
    response = api.get("/api/machines/machine1/config")
    assert response.status_code == 200
    assert response.json() == {"config": {}}

    # get jsonschema for machine
    response = api.get("/api/machines/machine1/schema")
    assert response.status_code == 200
    json_response = response.json()
    assert "schema" in json_response and "properties" in json_response["schema"]

    # set some config
    config = dict(
        clan=dict(
            jitsi=dict(
                enable=True,
            ),
        ),
        fileSystems={
            "/": dict(
                device="/dev/fake_disk",
                fsType="ext4",
            ),
        },
        # set boot.loader.grub.devices
        boot=dict(
            loader=dict(
                grub=dict(
                    devices=["/dev/fake_disk"],
                ),
            ),
        ),
    )
    response = api.put(
        "/api/machines/machine1/config",
        json=config,
    )
    assert response.status_code == 200
    assert response.json() == {"config": config}

    # verify the machine config
    response = api.get("/api/machines/machine1/verify")
    assert response.status_code == 200
    assert response.json() == {"success": True, "error": None}

    # get the config again
    response = api.get("/api/machines/machine1/config")
    assert response.status_code == 200
    assert response.json() == {"config": config}
