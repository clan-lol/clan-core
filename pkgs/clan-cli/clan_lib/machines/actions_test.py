from collections.abc import Callable
from typing import cast

import pytest

from clan_lib.flake import Flake
from clan_lib.nix_models.clan import Clan, Unknown

from .actions import list_machines


@pytest.mark.with_core
def test_list_nixos_machines(clan_flake: Callable[..., Flake]) -> None:
    clan_config: Clan = {
        "machines": {
            "jon": cast(Unknown, {}),  # Nixos Modules are not type checkable
            "sara": cast(Unknown, {}),  # Nixos Modules are not type checkable
        }
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
            }
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
