from collections.abc import Callable

import pytest

from clan_lib.flake import Flake

from .actions import MachineTag, list_inventory_tags


@pytest.mark.with_core
def test_list_inventory_tags(clan_flake: Callable[..., Flake]) -> None:
    flake = clan_flake(
        {
            "inventory": {
                "machines": {
                    "jon": {
                        # machineClass defaults to nixos
                        "tags": ["foo", "bar"],
                    },
                    "sara": {
                        "machineClass": "darwin",
                        "tags": ["foo", "baz", "fizz"],
                    },
                    "bob": {
                        "machineClass": "nixos",
                        "tags": ["foo", "bar"],
                    },
                },
            }
        },
    )

    tags = list_inventory_tags(flake)

    assert tags == [
        MachineTag(name="all", readonly=True),
        MachineTag(name="bar", readonly=False),
        MachineTag(name="baz", readonly=False),
        MachineTag(name="darwin", readonly=True),
        MachineTag(name="fizz", readonly=False),
        MachineTag(name="foo", readonly=False),
        MachineTag(name="nixos", readonly=True),
    ]


@pytest.mark.with_core
def test_list_inventory_tags_defaults(clan_flake: Callable[..., Flake]) -> None:
    flake = clan_flake(
        {
            "inventory": {
                "machines": {
                    "jon": {
                        # machineClass defaults to nixos
                    },
                    "sara": {
                        "machineClass": "darwin",
                    },
                    "bob": {
                        "machineClass": "nixos",
                    },
                },
            }
        },
    )

    tags = list_inventory_tags(flake)

    assert tags == [
        MachineTag(name="all", readonly=True),
        MachineTag(name="darwin", readonly=True),
        MachineTag(name="nixos", readonly=True),
    ]
