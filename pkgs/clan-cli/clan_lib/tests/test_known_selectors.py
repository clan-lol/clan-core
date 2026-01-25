from collections.abc import Callable
from typing import TYPE_CHECKING

import pytest

from clan_lib import nix_selectors
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.actions import list_machines

if TYPE_CHECKING:
    from clan_lib.nix_models.typing import (
        ClanInput,
    )


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

    # Test static selectors
    for static_selector_fn in nix_selectors.STATIC_SELECTORS:
        selector_str = static_selector_fn()
        try:
            flake.select(selector_str)
        except ClanError as e:
            pytest.fail(
                f"Static selector '{static_selector_fn.__name__}' failed\n"
                f"  Selector: {selector_str}\n"
                f"  Error: {e}"
            )

    # Test combinations
    test_pairs = [
        # darwin machines
        ("aarch64-darwin", "sara"),
        # linux machines
        ("x86_64-linux", "jon"),
    ]
    for system, machine_name in test_pairs:
        # Test
        for machine_selector_fn in nix_selectors.MACHINE_SELECTORS:
            selector_str = machine_selector_fn(system, machine_name)
            try:
                flake.select(selector_str)
            except ClanError as e:
                pytest.fail(
                    f"Machine selector '{machine_selector_fn.__name__}' failed\n"
                    f"  Selector: {selector_str}\n"
                    f"  Error: {e}"
                )

        generator_name = "testgen"

        if machine_name == "sara":
            # Skip darwin tests for vars:
            # Problem: cannot "build" darwin 'finalScript' on a linux host
            # nix-select tries to "nix build" it, which is a bit too much
            # This is an architecture flaw of nix-select
            # Fix this:
            # Failed: Generator selector 'generator_final_script' failed
            #  Selector: clanInternals.machines.aarch64-darwin.sara.config.clan.core.vars.generators."testgen".finalScript
            #  Error: Error on: $ clan select 'clanInternals.machines.aarch64-darwin.sara.config.clan.core.vars.generators."testgen".finalScript'
            #  Reason: Cannot build '/nix/store/446shaypn9ks936wz5v74ha0a4r5l3yf-generator-testgen.drv'.. Use flag '--debug' to see full nix trace.
            continue

        for generator_selector_fn in nix_selectors.GENERATOR_SELECTORS:
            selector_str = generator_selector_fn(system, machine_name, generator_name)
            try:
                flake.select(selector_str)
            except ClanError as e:
                pytest.fail(
                    f"Generator selector '{generator_selector_fn.__name__}' failed\n"
                    f"  Selector: {selector_str}\n"
                    f"  Error: {e}"
                )
