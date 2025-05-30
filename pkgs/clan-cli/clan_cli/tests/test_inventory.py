from clan_lib.nix_models.clan import Inventory
from clan_lib.nix_models.clan import InventoryMachine as Machine
from clan_lib.nix_models.clan import InventoryMeta as Meta
from clan_lib.nix_models.clan import InventoryService as Service


def test_make_meta_minimal() -> None:
    # Name is required
    res = Meta(
        {
            "name": "foo",
        }
    )

    assert res == {"name": "foo"}


def test_make_inventory_minimal() -> None:
    # Meta is required
    res = Inventory(
        {
            "meta": Meta(
                {
                    "name": "foo",
                }
            ),
        }
    )

    assert res == {"meta": {"name": "foo"}}


def test_make_machine_minimal() -> None:
    # Empty is valid
    res = Machine({})

    assert res == {}


def test_make_service_minimal() -> None:
    # Empty is valid
    res = Service({})

    assert res == {}
