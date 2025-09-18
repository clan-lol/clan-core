import time
from collections.abc import Callable
from typing import cast
from unittest.mock import ANY, patch

import pytest

from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines import actions as actions_module
from clan_lib.machines.machines import Machine
from clan_lib.nix_models.clan import (
    Clan,
    InventoryMachine,
    InventoryMachineTagsType,
    Unknown,
)
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import get_value_by_path, set_value_by_path

from .actions import (
    MachineState,
    MachineStatus,
    get_machine,
    get_machine_fields_schema,
    get_machine_state,
    list_machine_state,
    list_machines,
    set_machine,
)


@pytest.mark.with_core
def test_list_nixos_machines(clan_flake: Callable[..., Flake]) -> None:
    clan_config: Clan = {
        "machines": {
            "jon": cast("Unknown", {}),  # Nixos Modules are not type checkable
            "sara": cast("Unknown", {}),  # Nixos Modules are not type checkable
        },
    }
    flake = clan_flake(clan_config)

    machines = list_machines(flake)

    assert list(machines.keys()) == ["jon", "sara"]


@pytest.mark.with_core
def test_list_inventory_machines(clan_flake: Callable[..., Flake]) -> None:
    flake = clan_flake(
        {
            "inventory": {
                "machines": {
                    "jon": {},
                    "sara": {},
                },
            },
        },
        # Attention: This is a raw Nix expression, which is not type-checked in python
        # Use with care!
        raw=r"""
        {
            machines = {
                vanessa = { pkgs, ...}: { environment.systemPackages = [ pkgs.firefox ]; }; # Raw NixosModule
            };
        }
        """,
    )

    machines = list_machines(flake)

    assert list(machines.keys()) == ["jon", "sara", "vanessa"]


@pytest.mark.with_core
def test_list_machines_instance_refs(clan_flake: Callable[..., Flake]) -> None:
    flake = clan_flake(
        {
            "inventory": {
                "machines": {
                    "jon": {},
                    "sara": {},
                },
                "instances": {
                    "admin": {
                        "roles": {"default": {"machines": {"jon": {}}}},
                    },
                    "borgbackup": {
                        "roles": {"default": {"tags": {"all": {}}}},
                    },
                },
            },
        },
    )

    machines = list_machines(flake)

    assert machines["sara"].instance_refs == set({"borgbackup"})
    assert machines["jon"].instance_refs == set({"admin", "borgbackup"})


@pytest.mark.with_core
def test_set_machine_no_op(clan_flake: Callable[..., Flake]) -> None:
    flake = clan_flake(
        # clan.nix, cannot be changed
        clan={
            "inventory": {
                "machines": {
                    "jon": {},
                    "sara": {},
                },
            },
        },
    )

    # No-op roundtrip should not change anything in the inventory
    machine_jon = get_machine(flake, "jon")

    with patch(f"{actions_module.__name__}.InventoryStore._write") as mock_write:
        set_machine(Machine("jon", flake), machine_jon)

        # Assert _write was never called
        mock_write.assert_not_called()

        # Change something to make sure the mock_write is actually called
        machine_jon["machineClass"] = "darwin"
        set_machine(Machine("jon", flake), machine_jon)

        # This is a bit internal - we want to make sure the write is called
        # with only the changed value, so we don't persist the whole machine
        mock_write.assert_called_once_with(
            {"machines": {"jon": {"machineClass": "darwin"}}},
            post_write=ANY,
        )


@pytest.mark.with_core
def test_set_machine_fully_defined_in_nix(clan_flake: Callable[..., Flake]) -> None:
    flake = clan_flake(
        # clan.nix, cannot be changed
        clan={
            "inventory": {
                "machines": {
                    "jon": {
                        "machineClass": "nixos",
                        "description": "A NixOS machine",
                        "icon": "nixos",
                        "deploy": {
                            "targetHost": "jon.example.com",
                            "buildHost": "jon.example.com",
                        },
                        "tags": ["server", "backup"],
                    },
                },
            },
        },
    )

    # No-op roundtrip should not change anything in the inventory
    machine_jon = get_machine(flake, "jon")
    machine_jon["description"] = "description updated"

    with patch(f"{actions_module.__name__}.InventoryStore._write") as mock_write:
        with pytest.raises(ClanError) as exc_info:
            set_machine(Machine("jon", flake), machine_jon)

        assert (
            "Key 'machines.jon.description' is not writeable. It seems its value is statically defined in nix."
            in str(exc_info.value)
        )

        # Assert _write should not be called
        mock_write.assert_not_called()


@pytest.mark.with_core
def test_set_machine_manage_tags(clan_flake: Callable[..., Flake]) -> None:
    """Test adding/removing tags on a machine with validation of immutable base tags."""
    flake = clan_flake(
        clan={
            "inventory": {
                "machines": {
                    "jon": {"tags": ["nix1", "nix2"]},
                },
            },
        },
    )

    def get_jon() -> InventoryMachine:
        return get_machine(flake, "jon")

    def set_jon(tags: list[str]) -> None:
        machine = get_jon()
        machine["tags"] = tags
        set_machine(Machine("jon", flake), machine)

    # --- Add UI tags ---
    initial_tags = get_jon().get("tags", [])
    new_tags = [*initial_tags, "ui1", "ui2"]
    set_jon(new_tags)

    updated_tags = get_jon().get("tags", [])
    expected_tags = ["nix1", "nix2", "ui1", "ui2", "all", "nixos"]
    assert updated_tags == expected_tags

    # --- Remove UI tags (allowed) ---
    allowed_removal_tags = ["nix1", "nix2", "all", "nixos"]
    set_jon(allowed_removal_tags)
    assert get_jon().get("tags", []) == allowed_removal_tags

    # --- Attempt to remove mandatory tags (should raise) ---
    invalid_tags = ["all", "nixos"]  # Removing 'nix1', 'nix2' is disallowed
    with pytest.raises(ClanError) as exc_info:
        set_jon(invalid_tags)

    assert "Key 'machines.jon.tags' doesn't contain items ['nix1', 'nix2']" in str(
        exc_info.value,
    )


@pytest.mark.with_core
def test_get_machine_writeability(clan_flake: Callable[..., Flake]) -> None:
    flake = clan_flake(
        clan={
            "inventory": {
                "machines": {
                    "jon": {
                        "machineClass": "nixos",  # Static string is not writeable
                        "deploy": {},  # Empty dict is writeable
                        # TOOD: Return writability for existing items
                        "tags": ["nix1"],  # Static list is not partially writeable
                    },
                },
            },
        },
    )

    # TODO: Move this into the api
    inventory_store = InventoryStore(flake=flake)
    inventory = inventory_store.read()
    curr_tags = get_value_by_path(
        inventory, "machines.jon.tags", [], InventoryMachineTagsType
    )
    new_tags = ["managed1", "managed2"]
    set_value_by_path(inventory, "machines.jon.tags", [*curr_tags, *new_tags])
    inventory_store.write(inventory, message="Test writeability")

    # Check that the tags were updated
    persisted = inventory_store._get_persisted()
    assert get_value_by_path(persisted, "machines.jon.tags", []) == new_tags

    write_info = get_machine_fields_schema(Machine("jon", flake))

    # {'tags': {'writable': True, 'reason': None}, 'machineClass': {'writable': False, 'reason': None}, 'name': {'writable': False, 'reason': None}, 'description': {'writable': True, 'reason': None}, 'deploy.buildHost': {'writable': True, 'reason': None}, 'icon': {'writable': True, 'reason': None}, 'deploy.targetHost': {'writable': True, 'reason': None}}
    writeable_fields = {
        field for field, info in write_info.items() if not info["readonly"]
    }
    read_only_fields = {field for field, info in write_info.items() if info["readonly"]}

    assert writeable_fields == {
        "tags",
        "deploy.targetHost",
        "deploy.buildHost",
        "description",
        "icon",
        "installedAt",
    }
    assert read_only_fields == {"machineClass", "name"}

    assert write_info["tags"]["readonly_members"] == ["nix1", "all", "nixos"]


@pytest.mark.with_core
def test_machine_state(clan_flake: Callable[..., Flake]) -> None:
    now = int(time.time())
    yesterday = now - 86400
    last_week = now - 604800

    flake = clan_flake(
        # clan.nix, cannot be changed
        clan={
            "inventory": {
                "machines": {
                    "jon": {},
                    "sara": {"installedAt": yesterday},
                    "bob": {"installedAt": last_week},
                },
            },
        },
    )

    assert list_machine_state(flake) == {
        "jon": MachineState(status=MachineStatus.NOT_INSTALLED),
        "sara": MachineState(status=MachineStatus.OFFLINE),
        "bob": MachineState(status=MachineStatus.OFFLINE),
    }

    assert get_machine_state(Machine("jon", flake)) == MachineState(
        status=MachineStatus.NOT_INSTALLED,
    )
    assert get_machine_state(Machine("sara", flake)) == MachineState(
        status=MachineStatus.OFFLINE,
    )
    assert get_machine_state(Machine("bob", flake)) == MachineState(
        status=MachineStatus.OFFLINE,
    )
