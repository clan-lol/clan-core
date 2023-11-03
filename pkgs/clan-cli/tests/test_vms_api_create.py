import os
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

import pytest
from api import TestClient
from cli import Cli
from fixtures_flakes import FlakeForTest, create_flake
from httpx import SyncByteStream
from pydantic import AnyUrl
from root import CLAN_CORE

from clan_cli.types import FlakeName

if TYPE_CHECKING:
    from age_keys import KeyPair


@pytest.fixture
def flake_with_vm_with_secrets(
    monkeypatch: pytest.MonkeyPatch, temporary_home: Path
) -> Iterator[FlakeForTest]:
    yield from create_flake(
        monkeypatch,
        temporary_home,
        FlakeName("test_flake_with_core_dynamic_machines"),
        CLAN_CORE,
        machines=["vm_with_secrets"],
    )


@pytest.fixture
def remote_flake_with_vm_without_secrets(
    monkeypatch: pytest.MonkeyPatch, temporary_home: Path
) -> Iterator[FlakeForTest]:
    yield from create_flake(
        monkeypatch,
        temporary_home,
        FlakeName("test_flake_with_core_dynamic_machines"),
        CLAN_CORE,
        machines=["vm_without_secrets"],
        remote=True,
    )


def generic_create_vm_test(api: TestClient, flake: Path | AnyUrl, vm: str) -> None:
    print(f"flake_url: {flake} ")
    response = api.post(
        "/api/vms/create",
        json=dict(
            flake_url=str(flake),
            flake_attr=vm,
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
        print(line.decode("utf-8"))
    print("=========END LOGS==========")
    assert response.status_code == 200, "Failed to get vm logs"
    print("Get /api/vms/{uuid}/status")
    response = api.get(f"/api/vms/{uuid}/status")
    print("Finished Get /api/vms/{uuid}/status")
    assert response.status_code == 200, "Failed to get vm status"
    data = response.json()
    assert (
        data["status"] == "FINISHED"
    ), f"Expected to be finished, but got {data['status']} ({data})"


@pytest.mark.skipif(not os.path.exists("/dev/kvm"), reason="Requires KVM")
@pytest.mark.impure
def test_create_local(
    api: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    flake_with_vm_with_secrets: FlakeForTest,
    age_keys: list["KeyPair"],
) -> None:
    monkeypatch.setenv("SOPS_AGE_KEY", age_keys[0].privkey)
    cli = Cli()
    cmd = [
        "secrets",
        "users",
        "add",
        "user1",
        age_keys[0].pubkey,
        flake_with_vm_with_secrets.name,
    ]
    cli.run(cmd)

    generic_create_vm_test(api, flake_with_vm_with_secrets.path, "vm_with_secrets")


@pytest.mark.skipif(not os.path.exists("/dev/kvm"), reason="Requires KVM")
@pytest.mark.impure
def test_create_remote(
    api: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    remote_flake_with_vm_without_secrets: FlakeForTest,
) -> None:
    generic_create_vm_test(
        api, remote_flake_with_vm_without_secrets.path, "vm_without_secrets"
    )


# TODO: We need a test that creates the same VM twice, and checks that the second time it fails


# TODO: Democlan needs a machine called testVM, which is headless and gets executed by this test below
# pytest -n0 -s tests/test_vms_api_create.py::test_create_from_democlan
# @pytest.mark.skipif(not os.path.exists("/dev/kvm"), reason="Requires KVM")
# @pytest.mark.impure
# def test_create_from_democlan(
#     api: TestClient,
#     test_democlan_url: AnyUrl) -> None:
#         generic_create_vm_test(
#             api, test_democlan_url, "defaultVM"
#         )
