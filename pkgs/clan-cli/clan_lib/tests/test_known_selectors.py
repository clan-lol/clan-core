import contextlib
from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest

from clan_lib import nix_selectors
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.actions import list_machines
from clan_lib.nix import nix_config

if TYPE_CHECKING:
    from clan_lib.nix_models.typing import (
        ClanInput,
    )


@pytest.mark.broken_on_darwin
@pytest.mark.with_core
def test_known_selectors_exist(clan_flake: Callable[..., Flake]) -> None:
    """Test that every selector"""
    clan_config: ClanInput = {
        "inventory": {
            "meta": {"name": "test-clan"},
            "machines": {
                "jon": {},
                "sara": {"machineClass": "darwin"},
            },
        }
    }

    raw_clan = r"""
    let
        generator = {
            files.password.deploy = false;

            prompts.password.display = {
            group = "User";
            label = "Password";
            required = false;
            helperText = ''
                Your password will be encrypted and stored securely using the secret store you've configured.
            '';
            };

            prompts.password.type = "hidden";
            prompts.password.persist = true;
            prompts.password.description = "Leave empty to generate automatically";

            script = ''
            echo "login" > $out/password
            '';
        };
    in
    {
        # Minimal system configuration
        machines.jon = {
            system.stateVersion = "25.11";
            nixpkgs.hostPlatform = "x86_64-linux";
            clan.core.vars.generators.testgen = generator;
        };
        machines.sara = {
            system.stateVersion = 5;
            nixpkgs.hostPlatform = "aarch64-darwin";
            clan.core.vars.generators.testgen = generator;
        };
    }
    """

    flake = clan_flake(clan_config, raw_clan)
    machines = list_machines(flake)
    assert list(machines.keys()) == ["jon", "sara"]

    config = nix_config()
    system = config["system"]
    generator_name = "testgen"

    # Build the full list of selectors first so we can resolve them in a
    # single nix invocation. Selecting one at a time spawns a fresh nix
    # build per selector (~10s each on a busy CI builder).
    selectors: list[tuple[str, str]] = [
        (fn.__name__, fn()) for fn in nix_selectors.STATIC_SELECTORS
    ]
    selectors += [
        (fn.__name__, fn("Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU", "*"))
        for fn in nix_selectors.MODULE_SELECTORS
    ]
    for machine_name in machines:
        selectors += [
            (fn.__name__, fn(system, machine_name))
            for fn in nix_selectors.MACHINE_SELECTORS
        ]
        selectors += [
            (fn.__name__, fn(system, machine_name, generator_name))
            for fn in nix_selectors.GENERATOR_SELECTORS
        ]
    selectors += [
        (fn.__name__, fn(system, list(machines)))
        for fn in nix_selectors.MACHINES_SELECTORS
    ]

    # Try to resolve everything in one nix build. If that succeeds, the
    # per-selector loop below is just cache lookups. If it fails, fall back
    # to one-by-one so the failure points at the offending selector.
    with contextlib.suppress(ClanError):
        flake.precache([sel for _, sel in selectors])

    for name, selector_str in selectors:
        try:
            flake.select(selector_str)
        except ClanError as e:
            pytest.fail(
                f"Selector '{name}' failed\n  Selector: {selector_str}\n  Error: {e}"
            )
