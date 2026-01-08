from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest
from clan_cli.tests.fixtures_flakes import nested_dict
from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.services.modules import (
    delete_service_instance,
    get_service_readmes,
    list_service_instances,
    list_service_modules,
    set_service_instance,
)

if TYPE_CHECKING:
    from clan_lib.nix_models.typing import ClanInput, InventoryInput


@pytest.mark.with_core
def test_list_service_instances(
    clan_flake: Callable[..., Flake],
) -> None:
    # ATTENTION! This method lacks Typechecking
    config = nested_dict()
    # explicit module selection
    # We use this random string in test to avoid code dependencies on the input name
    config["inventory"]["instances"]["foo"]["module"]["input"] = (
        "Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU"
    )
    config["inventory"]["instances"]["foo"]["module"]["name"] = "sshd"
    # input = null
    config["inventory"]["instances"]["bar"]["module"]["input"] = None
    config["inventory"]["instances"]["bar"]["module"]["name"] = "sshd"

    # Omit input
    config["inventory"]["instances"]["baz"]["module"]["name"] = "sshd"
    # external input
    flake = clan_flake(config)

    service_modules = list_service_modules(flake)

    assert len(service_modules.modules)
    assert any(m.usage_ref.get("name") == "sshd" for m in service_modules.modules)

    instances = list_service_instances(flake)

    assert set(instances.keys()) == {"foo", "bar", "baz"}

    # Reference to a built-in module
    assert instances["foo"].resolved.usage_ref.get("input") is None
    assert instances["foo"].resolved.usage_ref.get("name") == "sshd"
    assert instances["foo"].resolved.info.manifest.name == "clan-core/sshd"
    # Actual module
    assert (
        instances["foo"].module.get("input")
        == "Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU"
    )

    # Module exposes the input name?
    assert instances["bar"].resolved.usage_ref.get("input") is None
    assert instances["bar"].resolved.usage_ref.get("name") == "sshd"

    assert instances["baz"].resolved.usage_ref.get("input") is None
    assert instances["baz"].resolved.usage_ref.get("name") == "sshd"

    borgbackup_service = next(
        m for m in service_modules.modules if m.usage_ref.get("name") == "borgbackup"
    )
    # Module has roles with descriptions
    assert borgbackup_service.info.roles["client"].description is not None
    assert borgbackup_service.info.roles["server"].description is not None


@pytest.mark.with_core
def test_get_service_readmes(
    clan_flake: Callable[..., Flake],
) -> None:
    clan_config: ClanInput = {}
    flake = clan_flake(clan_config)

    service_modules = list_service_modules(flake)
    service_names = [m.usage_ref["name"] for m in service_modules.modules]  # type: ignore[reportTypedDictNotRequiredAccess]

    collection = get_service_readmes(
        input_name=None,
        service_names=service_names,
        flake=flake,
    )

    assert collection.input_name is None
    assert collection.readmes["borgbackup"]
    assert len(collection.readmes["borgbackup"]) > 10


@pytest.mark.with_core
def test_list_service_modules(
    clan_flake: Callable[..., Flake],
) -> None:
    # Nice! This is typechecked :)
    clan_config: ClanInput = {
        "inventory": {
            "meta": {"name": "testclan"},
            "instances": {
                # No module spec -> resolves to clan-core/admin
                "admin": {},
                # Partial module spec
                "admin2": {"module": {"name": "admin"}},
                # Full explicit module spec
                "admin3": {
                    "module": {
                        "name": "admin",
                        "input": "Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU",
                    }
                },
            },
        }
    }
    flake = clan_flake(clan_config)

    service_modules = list_service_modules(flake)

    # Detects the input name right
    assert service_modules.core_input_name == "Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU"
    assert len(service_modules.modules)

    admin_service = next(
        m for m in service_modules.modules if m.usage_ref.get("name") == "admin"
    )
    assert admin_service

    assert admin_service.usage_ref == {"name": "admin", "input": None}
    assert set(admin_service.instance_refs) == {"admin", "admin2", "admin3"}

    # Negative test: Assert not used
    sshd_service = next(
        m for m in service_modules.modules if m.usage_ref.get("name") == "sshd"
    )
    assert sshd_service
    assert sshd_service.usage_ref == {"name": "sshd", "input": None}
    assert set(sshd_service.instance_refs) == set({})


@pytest.mark.with_core
def test_update_service_instance(
    clan_flake: Callable[..., Flake],
) -> None:
    # Data that can be mutated via API calls
    mutable_inventory_json: InventoryInput = {
        "instances": {
            "hello-world": {
                "roles": {
                    "morning": {
                        "machines": {
                            "jon": {
                                "settings": {  # type: ignore[typeddict-item]
                                    "greeting": "jon",
                                },
                            },
                            "sara": {
                                "settings": {  # type: ignore[typeddict-item]
                                    "greeting": "sara",
                                },
                            },
                        },
                        "tags": {
                            "all": {},
                        },
                        "settings": {  # type: ignore[typeddict-item]
                            "greeting": "hello",
                        },
                    }
                }
            }
        }
    }
    flake = clan_flake({}, mutable_inventory_json=mutable_inventory_json)

    # Ensure preconditions
    instances = list_service_instances(flake)
    assert set(instances.keys()) == {"hello-world"}

    # Wrong instance
    with pytest.raises(ClanError) as excinfo:
        set_service_instance(
            flake,
            "admin",
            {},
        )
    assert "Instance 'admin' not found" in str(excinfo.value)

    # Wrong roles
    with pytest.raises(ClanError) as excinfo:
        set_service_instance(
            flake,
            "hello-world",
            {"default": {"machines": {}}},
        )
    assert "Role 'default' cannot be used" in str(excinfo.value)

    # Remove 'settings' from jon machine
    set_service_instance(
        flake,
        "hello-world",
        {
            "morning": {
                "machines": {
                    "jon": {
                        "settings": {},  # type: ignore[typeddict-item]
                    },
                    "sara": {
                        "settings": {  # type: ignore[typeddict-item]
                            "greeting": "sara",
                        },
                    },
                },
                # Remove tags and settings from role
                "tags": {},
                "settings": {},  # type: ignore[typeddict-item]
            }
        },
    )

    updated_instances = list_service_instances(flake)
    updated_machines = (
        updated_instances["hello-world"].roles.get("morning", {}).get("machines", {})
    )

    assert updated_machines == {
        "jon": {"settings": {}},
        "sara": {"settings": {"greeting": "sara"}},
    }

    # Remove jon
    set_service_instance(
        flake,
        "hello-world",
        {
            "morning": {
                "machines": {
                    "sara": {
                        "settings": {  # type: ignore[typeddict-item]
                            "greeting": "sara",
                        },
                    },
                },
                # Remove tags and settings from role
                "tags": {},
                "settings": {},  # type: ignore[typeddict-item]
            }
        },
    )

    updated_instances = list_service_instances(flake)
    updated_machines = (
        updated_instances["hello-world"].roles.get("morning", {}).get("machines", {})
    )

    assert updated_machines == {
        "sara": {"settings": {"greeting": "sara"}},
    }


@pytest.mark.with_core
def test_delete_service_instance(
    clan_flake: Callable[..., Flake],
) -> None:
    # Data that can be mutated via API calls
    mutable_inventory_json: InventoryInput = {
        "meta": {"name": "testclan"},
        "instances": {
            "to-remain": {"module": {"name": "admin"}},
            "to-delete": {"module": {"name": "admin"}},
        },
    }

    flake = clan_flake({}, mutable_inventory_json=mutable_inventory_json)

    # Ensure preconditions
    instances = list_service_instances(flake)
    assert set(instances.keys()) == {"to-delete", "to-remain"}

    # Raises for non-existing instance
    with pytest.raises(ClanError) as excinfo:
        delete_service_instance(flake, "non-existing-instance")
    assert "Instance 'non-existing-instance' not found" in str(excinfo.value)

    # Deletes instance
    delete_service_instance(flake, "to-delete")

    updated_instances = list_service_instances(flake)
    assert set(updated_instances.keys()) == {"to-remain"}


@pytest.mark.with_core
def test_delete_static_service_instance(
    clan_flake: Callable[..., Flake],
) -> None:
    # Data that can be mutated via API calls
    mutable_inventory_json: InventoryInput = {
        "meta": {"name": "testclan"},
        "instances": {
            "static": {"module": {"name": "admin"}},
        },
    }

    flake = clan_flake(
        {
            "inventory": {
                "instances": {
                    "static": {"roles": {"default": {}}},
                }
            }
        },
        mutable_inventory_json=mutable_inventory_json,
    )

    # Ensure preconditions
    instances = list_service_instances(flake)
    assert set(instances.keys()) == {"static"}

    # Raises for non-existing instance
    with pytest.raises(ClanError) as excinfo:
        delete_service_instance(flake, "static")

    # TODO: improve error message
    assert "Cannot delete path 'instances.static" in str(excinfo.value)


@pytest.mark.with_core
def test_inline_extra_modules(clan_flake: Callable[..., Flake]) -> None:
    """ExtraModules are excluded from serialization to allow arbitrary inlining"""
    # Data that can be mutated via API calls
    mutable_inventory_json: InventoryInput = {
        "meta": {"name": "testclan"},
        "instances": {
            "static": {"module": {"name": "admin"}},
        },
    }
    nix = r"""
    {
        inventory.instances.static = {
            roles.default.extraModules = [
                (_: { }) # non-serializable inline module
            ];
        };
    }
    """

    flake = clan_flake(
        {},
        raw=nix,
        mutable_inventory_json=mutable_inventory_json,
    )

    # Ensure preconditions
    instances = list_service_instances(flake)

    assert set(instances.keys()) == {"static"}
