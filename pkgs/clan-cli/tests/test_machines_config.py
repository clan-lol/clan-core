import time

import pytest
from fixtures_flakes import FlakeForTest

from clan_cli.config.machine import (
    config_for_machine,
    set_config_for_machine,
    verify_machine_config,
)
from clan_cli.config.schema import machine_schema
from clan_cli.inventory import Machine
from clan_cli.machines.create import create_machine
from clan_cli.machines.list import list_machines


@pytest.mark.with_core
def test_schema_for_machine(test_flake_with_core: FlakeForTest) -> None:
    schema = machine_schema(test_flake_with_core.path, config={})
    assert "properties" in schema


@pytest.mark.with_core
def test_create_machine_on_minimal_clan(test_flake_minimal: FlakeForTest) -> None:
    assert list_machines(test_flake_minimal.path) == {}

    create_machine(
        test_flake_minimal.path,
        Machine(
            name="foo",
            system="x86_64-linux",
            description="A test machine",
            tags=["test"],
            icon=None,
        ),
    )

    st = time.time()
    result = list_machines(test_flake_minimal.path)
    et = time.time()
    elapsed = et - st
    # Listing should always take less than a second
    assert elapsed < 1

    assert list(result.keys()) == ["foo"]

    # Writes into settings.json
    set_config_for_machine(
        test_flake_minimal.path, "foo", dict(services=dict(openssh=dict(enable=True)))
    )

    config = config_for_machine(test_flake_minimal.path, "foo")
    assert config["services"]["openssh"]["enable"]
    assert verify_machine_config(test_flake_minimal.path, "foo") is None
