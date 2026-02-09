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

    # TODO: Test all modules
    for module_selector_fn in nix_selectors.MODULE_SELECTORS:
        selector_str = module_selector_fn(
            # clan-core
            "Y2xhbi1jaW9yZS1uZXZlci1kZXBlbmQtb24tbWU",
            "*",
        )
        try:
            flake.select(selector_str)
        except ClanError as e:
            pytest.fail(
                f"Machines selector '{module_selector_fn.__name__}' failed\n"
                f"  Selector: {selector_str}\n"
                f"  Error: {e}"
            )

    config = nix_config()
    system = config["system"]
    for machine_name in machines:
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

    # Select multiple machines
    for machines_selector_fn in nix_selectors.MACHINES_SELECTORS:
        selector_str = machines_selector_fn(system, list(machines))
        try:
            flake.select(selector_str)
        except ClanError as e:
            pytest.fail(
                f"Machines selector '{machines_selector_fn.__name__}' failed\n"
                f"  Selector: {selector_str}\n"
                f"  Error: {e}"
            )
