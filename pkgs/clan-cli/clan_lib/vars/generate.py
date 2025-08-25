import logging
from collections.abc import Callable

from clan_cli.vars.generator import Generator, GeneratorKey
from clan_cli.vars.graph import minimal_closure, requested_closure
from clan_cli.vars.migration import check_can_migrate, migrate_files

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine

log = logging.getLogger(__name__)


@API.register
def get_generators(
    machine: Machine,
    full_closure: bool,
    generator_name: str | None = None,
    include_previous_values: bool = False,
) -> list[Generator]:
    """Get generators for a machine, with optional closure computation.

    Args:
        machine: The machine to get generators for.
        full_closure: If True, include all dependency generators. If False, only include missing ones.
        generator_name: Name of a specific generator to get, or None for all generators.
        include_previous_values: If True, populate prompts with their previous values.

    Returns:
        List of generators based on the specified selection and closure mode.

    """
    from clan_cli.vars import graph

    vars_generators = Generator.get_machine_generators(machine.name, machine.flake)
    generators = {generator.key: generator for generator in vars_generators}

    result_closure = []
    if generator_name is None:  # all generators selected
        if full_closure:
            result_closure = graph.full_closure(generators)
        else:
            result_closure = graph.all_missing_closure(generators)
    # specific generator selected
    elif full_closure:
        gen_key = GeneratorKey(machine=machine.name, name=generator_name)
        result_closure = requested_closure([gen_key], generators)
    else:
        gen_key = GeneratorKey(machine=machine.name, name=generator_name)
        result_closure = minimal_closure([gen_key], generators)

    if include_previous_values:
        for generator in result_closure:
            for prompt in generator.prompts:
                prompt.previous_value = generator.get_previous_value(machine, prompt)

    return result_closure


def _ensure_healthy(
    machine: "Machine",
    generators: list[Generator] | None = None,
) -> None:
    """Run health checks on the provided generators.
    Fails if any of the generators' health checks fail.
    """
    if generators is None:
        generators = Generator.get_machine_generators(machine.name, machine.flake)

    pub_healtcheck_msg = machine.public_vars_store.health_check(
        machine.name,
        generators,
    )
    sec_healtcheck_msg = machine.secret_vars_store.health_check(
        machine.name,
        generators,
    )

    if pub_healtcheck_msg or sec_healtcheck_msg:
        msg = f"Health check failed for machine {machine.name}:\n"
        if pub_healtcheck_msg:
            msg += f"Public vars store: {pub_healtcheck_msg}\n"
        if sec_healtcheck_msg:
            msg += f"Secret vars store: {sec_healtcheck_msg}"
        raise ClanError(msg)


PromptFunc = Callable[[Generator], dict[str, str]]
"""Type for a function that collects prompt values for a generator.

The function receives a Generator and should return a dictionary mapping
prompt names to their values. This allows for custom prompt collection
strategies (e.g., interactive CLI, GUI, or programmatic).
"""


@API.register
def run_generators(
    machines: list[Machine],
    generators: str | list[str] | None = None,
    full_closure: bool = False,
    prompt_values: dict[str, dict[str, str]] | PromptFunc = lambda g: g.ask_prompts(),
    no_sandbox: bool = False,
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
        no_sandbox: Whether to disable sandboxing when executing the generator.

    Raises:
        ClanError: If the machine or generator is not found, or if there are issues with
        executing the generator.

    """
    for machine in machines:
        if isinstance(generators, list):
            # List of generator names - use them exactly as provided
            if len(generators) == 0:
                return
            # Create GeneratorKeys for this specific machine
            generator_keys = {
                GeneratorKey(machine=machine.name, name=name) for name in generators
            }
            all_generators = get_generators(machine, full_closure=True)
            generator_objects = [g for g in all_generators if g.key in generator_keys]
        else:
            # None or single string - use get_generators with closure parameter
            generator_objects = get_generators(
                machine,
                full_closure=full_closure,
                generator_name=generators,
            )

        # If prompt function provided, ask all prompts
        # TODO: make this more lazy and ask for every generator on execution
        if callable(prompt_values):
            prompt_values = {
                generator.name: prompt_values(generator)
                for generator in generator_objects
            }
        # execute health check
        _ensure_healthy(machine=machine, generators=generator_objects)

        # execute generators
        for generator in generator_objects:
            if check_can_migrate(machine, generator):
                migrate_files(machine, generator)
            else:
                generator.execute(
                    machine=machine,
                    prompt_values=prompt_values.get(generator.name, {}),
                    no_sandbox=no_sandbox,
                )
