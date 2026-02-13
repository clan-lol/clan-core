import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.nix import current_system
from clan_lib.nix_selectors import (
    generator_final_script,
    secrets_age_plugins,
    vars_sops_default_groups,
)
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.vars import graph
from clan_lib.vars.generator import (
    Generator,
    get_machine_generators,
    get_machine_selectors,
)
from clan_lib.vars.prompt import ask
from clan_lib.vars.secret_modules import sops

if TYPE_CHECKING:
    from pathlib import Path

    from clan_lib.vars._types import GeneratorId


log = logging.getLogger(__name__)

debug_condition = False


@dataclass
class GeneratorPromptIdentifier:
    generator_name: str
    prompt_name: str


@dataclass
class GeneratorPromptValue:
    generator_name: str
    prompt_name: str
    value: str | None


@API.register
def get_generator_prompt_previous_values(
    machine: Machine,
    prompt_identifiers: list[GeneratorPromptIdentifier],
) -> list[GeneratorPromptValue]:
    """Get previous values for specific prompts.

    Args:
        machine: The machine to get previous values for
        prompt_identifiers: List of (generator_name, prompt_name) to fetch

    Returns:
        Previous values for the requested prompts.

    """
    generators = get_machine_generators([machine.name], machine.flake)
    results = []

    for identifier in prompt_identifiers:
        gen = next((g for g in generators if g.name == identifier.generator_name), None)
        if gen is None:
            msg = f"Generator '{identifier.generator_name}' not found for machine '{machine.name}'"
            raise ClanError(msg)

        prompt = next(
            (p for p in gen.prompts if p.name == identifier.prompt_name), None
        )
        if prompt is None:
            msg = f"Prompt '{identifier.prompt_name}' not found in generator '{identifier.generator_name}'"
            raise ClanError(msg)

        if not prompt.persist:
            # Non-persisted prompts have no previous value
            results.append(
                GeneratorPromptValue(
                    generator_name=identifier.generator_name,
                    prompt_name=identifier.prompt_name,
                    value=None,
                )
            )
            continue

        prev_value = gen.get_previous_value(prompt)
        results.append(
            GeneratorPromptValue(
                generator_name=identifier.generator_name,
                prompt_name=identifier.prompt_name,
                value=prev_value,
            )
        )

    return results


def get_generators_precache_selectors(machine_names: list[str]) -> list[str]:
    """Get all selectors needed for get_generators and run_generators.

    This function returns all selectors that should be precached before calling
    get_generators or run_generators. It includes inventory selectors, generator
    metadata, and execution-time selectors (finalScript, sops config).

    Args:
        machine_names: The names of machines to get selectors for.

    Returns:
        List of selectors to precache.

    """
    return InventoryStore.default_selectors() + get_machine_selectors(machine_names)


@API.register
def get_generators(
    machines: list[Machine],
    full_closure: bool,
    generator_name: str | None = None,
) -> list[Generator]:
    """Get generators for a machine, with optional closure computation.

    Args:
        machines: The machines to get generators for.
        full_closure: If True, include all dependency generators. If False, only include missing ones.
        generator_name: Name of a specific generator to get, or None for all generators.

    Returns:
        List of generators based on the specified selection and closure mode.

    """
    if not machines:
        msg = "At least one machine must be provided"
        raise ClanError(msg)
    flake = machines[0].flake
    all_machines = flake.list_machines().keys()
    flake.precache(get_generators_precache_selectors(list(all_machines)))
    requested_machines = [machine.name for machine in machines]

    # Cache decrypted secrets to avoid repeated decryption for shared generators
    secret_cache: dict[Path, bytes] = {}

    all_generators = get_machine_generators(
        all_machines,
        flake,
    )
    machines_generators = get_machine_generators(
        requested_machines,
        flake,
    )

    # Inject shared secret cache into all secret stores
    for gen in all_generators + machines_generators:
        if gen._secret_store is not None:  # noqa: SLF001
            gen._secret_store._secret_cache = secret_cache  # noqa: SLF001

    requested_generators = {
        generator.key: generator for generator in machines_generators
    }

    # Select root generators
    roots: list[GeneratorId]
    if generator_name is None:
        roots = list(requested_generators.keys())
    else:
        roots = [key for key in requested_generators if key.name == generator_name]

        # Abort if the generator is not found
        if not roots:
            msg = f"Generator '{generator_name}' not found in machines {requested_machines}"
            raise ClanError(msg)

    # Compute closure based on mode
    closure_func = (
        graph.requested_closure if full_closure else graph.all_missing_closure
    )
    return closure_func(
        roots, {generator.key: generator for generator in all_generators}
    )


def _ensure_healthy(
    machine: "Machine",
    generators: list[Generator] | None = None,
) -> None:
    """Run health checks on the provided generators.
    Fails if any of the generators' health checks fail.
    """
    if generators is None:
        generators = get_machine_generators([machine.name], machine.flake)

    public_health_check_msg = machine.public_vars_store.health_check(
        machine.name,
        generators,
    )
    secret_health_check_msg = machine.secret_vars_store.health_check(
        machine.name,
        generators,
    )

    if public_health_check_msg or secret_health_check_msg:
        msg = f"Health check failed for machine {machine.name}:\n"
        if public_health_check_msg:
            msg += f"Public vars store: {public_health_check_msg}\n"
        if secret_health_check_msg:
            msg += f"Secret vars store: {secret_health_check_msg}"
        raise ClanError(msg)


PromptFunc = Callable[[Generator], dict[str, str]]
"""Type for a function that collects prompt values for a generator.

The function receives a Generator and should return a dictionary mapping
prompt names to their values. This allows for custom prompt collection
strategies (e.g., interactive CLI, GUI, or programmatic).
"""


def _default_prompt_func(auto_accept_prompts: bool) -> PromptFunc:
    """Create a prompt function that optionally auto-accepts previous values.

    Args:
        auto_accept_prompts: If True, use previous values without asking when available.

    Returns:
        A prompt function suitable for run_generators.

    """

    def prompt_func(g: Generator) -> dict[str, str]:
        prompt_values: dict[str, str] = {}
        for prompt in g.prompts:
            previous_value = g.get_previous_value(prompt)
            # Auto-accept if enabled and previous value exists
            if auto_accept_prompts and previous_value is not None:
                prompt_values[prompt.name] = previous_value
            else:
                # Ask interactively
                var_id = f"{g.name}/{prompt.name}"
                prompt_values[prompt.name] = ask(
                    var_id,
                    prompt.prompt_type,
                    prompt.description if prompt.description != prompt.name else None,
                    g.machines,
                    previous_value=previous_value,
                )
        return prompt_values

    return prompt_func


@API.register
def run_generators(
    machines: list[Machine],
    generators: str | list[str] | None = None,
    full_closure: bool = False,
    prompt_values: dict[str, dict[str, str]] | PromptFunc | None = None,
    no_sandbox: bool = False,
    auto_accept_prompts: bool = False,
) -> None:
    """Run the specified generators for machines.

    Args:
        machines: The machines to run generators for.
        generators: Can be:
            - None: Run all generators (with closure based on full_closure parameter)
            - str: Single generator name to run (with closure based on full_closure parameter)
            - list[str]: Specific generator names to run exactly as provided.
                Dependency generators are not added automatically in this case.
                The caller must ensure that all dependencies are included.
        full_closure: Whether to include all dependencies (True) or only missing ones (False).
            Only used when generators is None or a string.
        prompt_values: A dictionary mapping generator names to their prompt values,
            or a function that returns prompt values for a generator.
            If None, uses the default prompt function.
        no_sandbox: Whether to disable sandboxing when executing the generator.
        auto_accept_prompts: If True, automatically use previous prompt values when
            available instead of asking interactively. Only applies when prompt_values
            is None (using default prompt function).

    Raises:
        ClanError: If the machine or generator is not found, or if there are issues with
        executing the generator.

    """
    if not machines:
        msg = "At least one machine must be provided"
        raise ClanError(msg)
    all_generators = get_generators(machines, full_closure=True)
    if isinstance(generators, list):
        # List of generator names - use them exactly as provided
        if len(generators) == 0:
            return
        generators_to_run = [g for g in all_generators if g.key.name in generators]
    else:
        # None or single string - use get_generators with closure parameter
        generators_to_run = get_generators(
            machines,
            full_closure=full_closure,
            generator_name=generators,
        )

    # Handle prompt values - can be None, callable, or dict
    # TODO: make this more lazy and ask for every generator on execution
    if prompt_values is None:
        # Use default prompt function with auto_accept_prompts setting
        prompt_func = _default_prompt_func(auto_accept_prompts)
        prompt_values = {
            generator.name: prompt_func(generator) for generator in generators_to_run
        }
    elif callable(prompt_values):
        prompt_values = {
            generator.name: prompt_values(generator) for generator in generators_to_run
        }

    # execute health check
    for machine in machines:
        _ensure_healthy(machine=machine)

    # get the flake via any machine (they are all the same)
    flake = machines[0].flake

    # preheat the select cache, to reduce repeated calls during execution
    selectors = [secrets_age_plugins()]
    for generator in generators_to_run:
        selectors.append(
            generator_final_script(
                current_system(), generator.machines[0], generator.name
            )
        )
        selectors.append(
            vars_sops_default_groups(current_system(), [generator.machines[0]])
        )
    flake.precache(selectors)

    # execute generators
    for generator in generators_to_run:
        if not generator.machines:
            continue
        generator.execute(
            machine_name=generator.machines[0],
            prompt_values=prompt_values.get(generator.name, {}),
            no_sandbox=no_sandbox,
        )

    # ensure all selected machines have access to all selected shared generators
    for generator in all_generators:
        if generator.share:
            for file in generator.files:
                if not file.secret or not file.exists or not file.deploy:
                    continue
                for machine in [
                    Machine(name=machine_name, flake=flake)
                    for machine_name in generator.machines
                ]:
                    # Workaround because of a poorly designed Store interface
                    # Recipients should always have access
                    # TODO: Introduce recipient interface into the StoreBase
                    if not isinstance(machine.secret_vars_store, sops.SecretStore):
                        continue
                    machine.secret_vars_store.ensure_machine_has_access(
                        generator,
                        file.name,
                        machine.name,
                    )
