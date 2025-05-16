import pytest
from clan_lib.flake.flake import Flake

from clan_cli.machines.machines import Machine

# Functions to test
from clan_cli.tests.fixtures_flakes import FlakeForTest


@pytest.mark.parametrize(
    "test_flake_with_core",
    [
        # Two nixos machines
        {
            "inventory_expr": r"""{
                machines.jon1 = { };
                machines.jon2 = { machineClass = "nixos"; };
                machines.sara = { machineClass = "darwin"; };
            }"""
        },
    ],
    # Important!
    # tells pytest to pass these values to the fixture
    # So we can write it to the flake fixtures
    indirect=True,
)
@pytest.mark.with_core
def test_inventory_machine_detect_class(
    test_flake_with_core: FlakeForTest,
) -> None:
    """
    Testing different inventory deserializations
    Inventory should always be deserializable to a dict
    """
    machine_jon1 = Machine(
        name="jon",
        flake=Flake(str(test_flake_with_core.path)),
    )
    machine_jon2 = Machine(
        name="jon2",
        flake=Flake(str(test_flake_with_core.path)),
    )
    machine_sara = Machine(
        name="sara",
        flake=Flake(str(test_flake_with_core.path)),
    )
    assert machine_jon1._class_ == "nixos"
    assert machine_jon2._class_ == "nixos"
    assert machine_sara._class_ == "darwin"
