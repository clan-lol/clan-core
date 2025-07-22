from collections.abc import Callable

import pytest

from clan_lib.flake import Flake

from .actions import list_machines


@pytest.mark.with_core
def test_list_nixos_machines(clan_flake: Callable[..., Flake]) -> None:
    flake = clan_flake(r"""
        {
            machines = {
                jon = { };
                sara = { };
            };
        }
        """)

    machines = list_machines(flake)

    assert list(machines.keys()) == ["jon", "sara"]


@pytest.mark.with_core
def test_list_inventory_machines(clan_flake: Callable[..., Flake]) -> None:
    flake = clan_flake(r"""
        {
            inventory.machines = {
                jon = { };
                sara = { };
            };
        }
        """)

    machines = list_machines(flake)

    assert list(machines.keys()) == ["jon", "sara"]
