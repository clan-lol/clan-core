import os
from pathlib import Path
from typing import TYPE_CHECKING, Iterator

import pytest
from api import TestClient
from cli import Cli
from fixtures_flakes import create_flake
from httpx import SyncByteStream
from root import CLAN_CORE

if TYPE_CHECKING:
    from age_keys import KeyPair


@pytest.fixture
def flake_with_vm_with_secrets(monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    yield from create_flake(
        monkeypatch,
        "test_flake_with_core_dynamic_machines",
        CLAN_CORE,
        machines=["vm_with_secrets"],
    )


@pytest.fixture
def remote_flake_with_vm_without_secrets(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[Path]:
    yield from create_flake(
        monkeypatch,
        "test_flake_with_core_dynamic_machines",
        CLAN_CORE,
        machines=["vm_without_secrets"],
        remote=True,
    )


@pytest.fixture
def create_user_with_age_key(
    monkeypatch: pytest.MonkeyPatch,
    age_keys: list["KeyPair"],
) -> None:
    monkeypatch.setenv("SOPS_AGE_KEY", age_keys[0].privkey)
    cli = Cli()
    cli.run(["secrets", "users", "add", "user1", age_keys[0].pubkey])


def generic_create_vm_test(api: TestClient, flake: Path, vm: str) -> None:
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

    response = api.get(f"/api/vms/{uuid}/status")
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
    flake_with_vm_with_secrets: Path,
    create_user_with_age_key: None,
) -> None:
    generic_create_vm_test(api, flake_with_vm_with_secrets, "vm_with_secrets")


@pytest.mark.skipif(not os.path.exists("/dev/kvm"), reason="Requires KVM")
@pytest.mark.impure
def test_create_remote(
    api: TestClient,
    monkeypatch: pytest.MonkeyPatch,
    remote_flake_with_vm_without_secrets: Path,
) -> None:
    generic_create_vm_test(
        api, remote_flake_with_vm_without_secrets, "vm_without_secrets"
    )
