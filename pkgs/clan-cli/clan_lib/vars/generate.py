import logging
from collections.abc import Callable

from clan_cli.vars import graph
from clan_cli.vars.generator import Generator
from clan_cli.vars.graph import requested_closure
from clan_cli.vars.migration import check_can_migrate, migrate_files
from clan_cli.vars.secret_modules import sops

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.persist.inventory_store import InventoryStore

log = logging.getLogger(__name__)

debug_condition = False


@API.register
def get_generators(
    machines: list[Machine],
    full_closure: bool,
    generator_name: str | None = None,
    include_previous_values: bool = False,
) -> list[Generator]:
    """Get generators for a machine, with optional closure computation.

    Args:
        machines: The machines to get generators for.
        full_closure: If True, include all dependency generators. If False, only include missing ones.
        generator_name: Name of a specific generator to get, or None for all generators.
        include_previous_values: If True, populate prompts with their previous values.

    Returns:
        List of generators based on the specified selection and closure mode.

    """
    if not machines:
        msg = "At least one machine must be provided"
        raise ClanError(msg)
    flake = machines[0].flake
    flake.precache(
        InventoryStore.default_selectors()
        + Generator.get_machine_selectors(m.name for m in machines)
    )
    all_machines = flake.list_machines().keys()
    requested_machines = [machine.name for machine in machines]

    all_generators_list = Generator.get_machine_generators(
        all_machines,
        flake,
        include_previous_values=include_previous_values,
    )
    requested_generators_list = Generator.get_machine_generators(
        requested_machines,
        flake,
        include_previous_values=include_previous_values,
    )

    all_generators = {generator.key: generator for generator in all_generators_list}
    requested_generators = {
        generator.key: generator for generator in requested_generators_list
    }

    result_closure = []
    if generator_name is None:  # all generators selected
        if full_closure:
            result_closure = graph.requested_closure(
                requested_generators.keys(), all_generators
            )
        else:
            result_closure = graph.all_missing_closure(
                requested_generators.keys(), all_generators
            )
    # specific generator selected
    elif full_closure:
        roots = [key for key in requested_generators if key.name == generator_name]
        result_closure = requested_closure(roots, all_generators)
    else:
        roots = [key for key in requested_generators if key.name == generator_name]
        result_closure = graph.all_missing_closure(roots, all_generators)

    return result_closure


def _ensure_healthy(
    machine: "Machine",
    generators: list[Generator] | None = None,
) -> None:
    """Run health checks on the provided generators.
    Fails if any of the generators' health checks fail.
    """
    if generators is None:
        generators = Generator.get_machine_generators([machine.name], machine.flake)

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

    # If prompt function provided, ask all prompts
    # TODO: make this more lazy and ask for every generator on execution
    if callable(prompt_values):
        prompt_values = {
            generator.name: prompt_values(generator) for generator in generators_to_run
        }

    # execute health check
    for machine in machines:
        _ensure_healthy(machine=machine)

    # ensure all selected machines have access to all selected shared generators
    for machine in machines:
        # This is only relevant for the sops store
        # TODO: improve store abstraction to use Protocols and introduce a proper SecretStore interface
        if not isinstance(machine.secret_vars_store, sops.SecretStore):
            continue
        for generator in all_generators:
            if generator.share:
                for file in generator.files:
                    if not file.secret or not file.exists or not file.deploy:
                        continue
                    machine.secret_vars_store.ensure_machine_has_access(
                        generator,
                        file.name,
                        machine.name,
                    )

    # get the flake via any machine (they are all the same)
    flake = machines[0].flake

    def get_generator_machine(generator: Generator) -> Machine:
        if generator.share:
            # return first machine if generator is shared
            return machines[0]
        return Machine(name=generator.machines[0], flake=flake)

    # preheat the select cache, to reduce repeated calls during execution
    selectors = []
    for generator in generators_to_run:
        machine = get_generator_machine(generator)
        selectors.append(generator.final_script_selector(machine.name))
    flake.precache(selectors)

    # execute generators
    for generator in generators_to_run:
        machine = get_generator_machine(generator)
        if check_can_migrate(machine, generator):
            migrate_files(machine, generator)
        else:
            generator.execute(
                machine=machine,
                prompt_values=prompt_values.get(generator.name, {}),
                no_sandbox=no_sandbox,
            )
