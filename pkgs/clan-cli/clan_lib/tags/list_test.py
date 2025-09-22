from collections.abc import Callable

import pytest

from clan_lib.flake import Flake
from clan_lib.nix_models.clan import InventoryMachineTagsType
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.path_utils import get_value_by_path, set_value_by_path
from clan_lib.tags.list import list_tags


@pytest.mark.with_core
def test_list_inventory_tags(clan_flake: Callable[..., Flake]) -> None:
    flake = clan_flake(
        {
            "inventory": {
                "machines": {
                    "jon": {
                        "tags": ["foo", "bar"],
                    },
                    "sara": {
                        "tags": ["foo", "baz", "fizz"],
                    },
                    "bob": {
                        "tags": ["foo", "bar"],
                    },
                },
                "instances": {
                    "instance1": {
                        "roles": {
                            "role1": {"tags": {"predefined": {}, "maybe": {}}},
                            "role2": {"tags": {"predefined2": {}, "maybe2": {}}},
                        }
                    },
                },
            }
        },
        raw=r"""
            {
                inventory.tags = {
                    "global" = [ "future_machine" ];
                };
            }
        """,
    )

    inventory_store = InventoryStore(flake=flake)
    inventory = inventory_store.read()
    curr_tags = get_value_by_path(
        inventory, "machines.jon.tags", [], InventoryMachineTagsType
    )
    new_tags = ["managed1", "managed2"]
    set_value_by_path(inventory, "machines.jon.tags", [*curr_tags, *new_tags])
    inventory_store.write(inventory, message="Test add tags via API")

    # Check that the tags were updated
    persisted = inventory_store._get_persisted()
    assert get_value_by_path(persisted, "machines.jon.tags", []) == new_tags

    tags = list_tags(flake)

    assert tags.options == set(
        {
            # Tags defined in nix
            "bar",
            "baz",
            "fizz",
            "foo",
            "predefined",
            "predefined2",
            "maybe",
            "maybe2",
            # Tags managed by the UI
            "managed1",
            "managed2",
        }
    )

    assert tags.special == set(
        {
            # Predefined tags
            "all",
            "global",
            "darwin",
            "nixos",
        }
    )
