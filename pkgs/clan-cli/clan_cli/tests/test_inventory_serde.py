from typing import Any, cast

import pytest
from clan_cli.flake import Flake
from clan_cli.tests.fixtures_flakes import FlakeForTest
from clan_lib.persist.inventory_store import InventoryStore


@pytest.mark.parametrize(
    "test_flake_with_core",
    [
        # Emtpy inventory
        {"inventory_expr": r"{ }"},
        # Empty machines
        {
            "inventory_expr": r"""{
                machines.jon = {};
                machines.sara = {};
            }"""
        },
        # TODO: Test
        # - Function modules
        # - Instances with non-deserializable settings ?
        # - Tags function modules
        # -
        # {
        #     "inventory_expr": r"""{
        #         modules.messager = { ... }: { };
        #     }"""
        # },
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=True,
)
@pytest.mark.with_core
def test_inventory_deserialize_variants(
    test_flake_with_core: FlakeForTest,
) -> None:
    """
    Testing different inventory deserializations
    Inventory should always be deserializable to a dict
    """
    inventory_store = InventoryStore(Flake(str(test_flake_with_core.path)))

    # Cast the inventory to a dict for the following assertions
    inventory = cast(dict[str, Any], inventory_store.read())

    # Check that the inventory is a dict
    assert isinstance(inventory, dict)

    # Check that all keys are present
    assert "meta" in inventory
    assert "machines" in inventory
    assert "services" in inventory
    assert "tags" in inventory
    assert "modules" in inventory
    assert "instances" in inventory
