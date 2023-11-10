import pytest
from api import TestClient
from fixtures_flakes import FlakeForTest


def test_machines(api: TestClient, test_flake: FlakeForTest) -> None:
    response = api.get(f"/api/{test_flake.name}/machines")
    assert response.status_code == 200
    assert response.json() == {"machines": []}

    response = api.post(f"/api/{test_flake.name}/machines", json={"name": "test"})
    assert response.status_code == 201

    assert response.json() == {"machine": {"name": "test", "status": "unknown"}}

    response = api.get(f"/api/{test_flake.name}/machines/test")
    assert response.status_code == 200
    assert response.json() == {"machine": {"name": "test", "status": "unknown"}}

    response = api.get(f"/api/{test_flake.name}/machines")
    assert response.status_code == 200
    assert response.json() == {"machines": [{"name": "test", "status": "unknown"}]}


@pytest.mark.with_core
def test_schema_errors(api: TestClient, test_flake_with_core: FlakeForTest) -> None:
    # make sure that eval errors do not raise an internal server error
    response = api.put(
        f"/api/{test_flake_with_core.name}/schema",
        json={"imports": ["some-inavlid-import"]},
    )
    assert response.status_code == 422
    assert (
        "error: string 'some-inavlid-import' doesn't represent an absolute path"
        in response.json()["detail"][0]["msg"]
    )


@pytest.mark.with_core
def test_schema_invalid_clan_imports(
    api: TestClient, test_flake_with_core: FlakeForTest
) -> None:
    response = api.put(
        f"/api/{test_flake_with_core.name}/schema",
        json={"clanImports": ["non-existing-clan-module"]},
    )
    assert response.status_code == 400
    assert (
        "Some requested clan modules could not be found"
        in response.json()["detail"]["msg"]
    )
    assert "non-existing-clan-module" in response.json()["detail"]["modules_not_found"]


def test_create_machine_invalid_hostname(
    api: TestClient, test_flake: FlakeForTest
) -> None:
    response = api.post(
        f"/api/{test_flake.name}/machines", json={"name": "-invalid-hostname"}
    )
    assert response.status_code == 422
    assert (
        "Machine name must be a valid hostname" in response.json()["detail"][0]["msg"]
    )


@pytest.mark.with_core
def test_configure_machine(api: TestClient, test_flake_with_core: FlakeForTest) -> None:
    # ensure error 404 if machine does not exist when accessing the config
    response = api.get(f"/api/{test_flake_with_core.name}/machines/machine1/config")
    assert response.status_code == 404

    # ensure error 404 if machine does not exist when writing to the config
    response = api.put(
        f"/api/{test_flake_with_core.name}/machines/machine1/config", json={}
    )
    assert response.status_code == 404

    # create the machine
    response = api.post(
        f"/api/{test_flake_with_core.name}/machines", json={"name": "machine1"}
    )
    assert response.status_code == 201

    # ensure an empty config is returned by default for a new machine
    response = api.get(f"/api/{test_flake_with_core.name}/machines/machine1/config")
    assert response.status_code == 200
    assert response.json() == {
        "clanImports": [],
        "clan": {},
    }

    # get jsonschema for without imports
    response = api.put(
        f"/api/{test_flake_with_core.name}/schema",
        json={"clanImports": []},
    )
    assert response.status_code == 200
    json_response = response.json()
    assert "schema" in json_response and "properties" in json_response["schema"]

    # an invalid config missing the fileSystems
    invalid_config = dict(
        clan=dict(),
        services=dict(
            nginx=dict(
                enable=True,
            ),
        ),
    )

    # verify an invalid config (fileSystems missing) fails
    response = api.put(
        f"/api/{test_flake_with_core.name}/machines/machine1/verify",
        json=invalid_config,
    )
    assert response.status_code == 200
    assert (
        "The ‘fileSystems’ option does not specify your root"
        in response.json()["error"]
    )

    # set come invalid config (fileSystems missing)
    response = api.put(
        f"/api/{test_flake_with_core.name}/machines/machine1/config",
        json=invalid_config,
    )
    assert response.status_code == 200

    # ensure the config has actually been updated
    response = api.get(f"/api/{test_flake_with_core.name}/machines/machine1/config")
    assert response.status_code == 200
    assert response.json() == dict(clanImports=[], **invalid_config)

    # the part of the config that makes the evaluation pass
    fs_config = dict(
        fileSystems={
            "/": dict(
                device="/dev/fake_disk",
                fsType="ext4",
            ),
        },
        boot=dict(
            loader=dict(
                grub=dict(
                    devices=["/dev/fake_disk"],
                ),
            ),
        ),
    )

    # set some valid config
    config2 = dict(
        clan=dict(),
        services=dict(
            nginx=dict(
                enable=True,
            ),
        ),
        **fs_config,
    )

    response = api.put(
        f"/api/{test_flake_with_core.name}/machines/machine1/config",
        json=config2,
    )
    assert response.status_code == 200

    # ensure the config has been applied
    response = api.get(
        f"/api/{test_flake_with_core.name}/machines/machine1/config",
    )
    assert response.status_code == 200
    assert response.json() == dict(clanImports=[], **config2)

    # get the config again
    response = api.get(f"/api/{test_flake_with_core.name}/machines/machine1/config")
    assert response.status_code == 200
    assert response.json() == {"clanImports": [], **config2}

    # ensure PUT on the config is idempotent by passing the config again
    # For example, this should not result in the boot.loader.grub.devices being
    #   set twice (eg. merged)
    response = api.put(
        f"/api/{test_flake_with_core.name}/machines/machine1/config",
        json=config2,
    )
    assert response.status_code == 200

    # ensure the config has been applied
    response = api.get(
        f"/api/{test_flake_with_core.name}/machines/machine1/config",
    )
    assert response.status_code == 200
    assert response.json() == dict(clanImports=[], **config2)

    # verify the machine config evaluates
    response = api.get(f"/api/{test_flake_with_core.name}/machines/machine1/verify")
    assert response.status_code == 200

    assert response.json() == {"success": True, "error": None}

    # get the schema with an extra module imported
    response = api.put(
        f"/api/{test_flake_with_core.name}/schema",
        json={"clanImports": ["diskLayouts"]},
    )
    # expect the result schema to contain the deltachat option
    assert response.status_code == 200
    assert (
        response.json()["schema"]["properties"]["diskLayouts"]["properties"][
            "singleDiskExt4"
        ]["properties"]["device"]["type"]
        == "string"
    )

    # new config importing an extra clanModule (clanModules.fake-module)
    config_with_imports: dict = {
        "clanImports": ["fake-module"],
        "clan": {
            "fake-module": {
                "fake-flag": True,
            },
        },
        **fs_config,
    }

    # set the fake-module.fake-flag option to true
    response = api.put(
        f"/api/{test_flake_with_core.name}/machines/machine1/config",
        json=config_with_imports,
    )
    assert response.status_code == 200

    # ensure the config has been applied
    response = api.get(
        f"/api/{test_flake_with_core.name}/machines/machine1/config",
    )
    assert response.status_code == 200
    assert response.json() == {
        "clanImports": ["fake-module"],
        "clan": {
            "fake-module": {
                "fake-flag": True,
            },
        },
        **fs_config,
    }

    # remove the import from the config
    config_with_empty_imports = dict(
        clanImports=[],
        **fs_config,
    )
    response = api.put(
        f"/api/{test_flake_with_core.name}/machines/machine1/config",
        json=config_with_empty_imports,
    )
    assert response.status_code == 200

    # ensure the config has been applied
    response = api.get(
        f"/api/{test_flake_with_core.name}/machines/machine1/config",
    )
    assert response.status_code == 200
    assert response.json() == {
        "clanImports": ["fake-module"],
        "clan": {},
        **config_with_empty_imports,
    }
