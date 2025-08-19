import argparse
import logging
from collections.abc import Callable
from typing import Literal

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_services_for_machine,
)
from clan_cli.vars.generator import Generator, GeneratorKey
from clan_cli.vars.migration import check_can_migrate, migrate_files
from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.flake import require_flake
from clan_lib.machines.list import list_full_machines
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_config

from .graph import minimal_closure, requested_closure

log = logging.getLogger(__name__)


@API.register
def get_generators(
    machine: Machine,
    full_closure: bool,
    generator_name: str | None = None,
    include_previous_values: bool = False,
) -> list[Generator]:
    """
    Get generators for a machine, with optional closure computation.

    Args:
        machine: The machine to get generators for.
        full_closure: If True, include all dependency generators. If False, only include missing ones.
        generator_name: Name of a specific generator to get, or None for all generators.
        include_previous_values: If True, populate prompts with their previous values.

    Returns:
        List of generators based on the specified selection and closure mode.
    """
    from . import graph

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
    """
    Run health checks on the provided generators.
    Fails if any of the generators' health checks fail.
    """
    if generators is None:
        generators = Generator.get_machine_generators(machine.name, machine.flake)

    pub_healtcheck_msg = machine.public_vars_store.health_check(
        machine.name, generators
    )
    sec_healtcheck_msg = machine.secret_vars_store.health_check(
        machine.name, generators
    )

    if pub_healtcheck_msg or sec_healtcheck_msg:
        msg = f"Health check failed for machine {machine.name}:\n"
        if pub_healtcheck_msg:
            msg += f"Public vars store: {pub_healtcheck_msg}\n"
        if sec_healtcheck_msg:
            msg += f"Secret vars store: {sec_healtcheck_msg}"
        raise ClanError(msg)


def _generate_vars_for_machine(
    machine: "Machine",
    generators: list[Generator],
    prompt_values: dict[str, dict[str, str]],
    no_sandbox: bool = False,
) -> None:
    _ensure_healthy(machine=machine, generators=generators)
    for generator in generators:
        if check_can_migrate(machine, generator):
            migrate_files(machine, generator)
        else:
            generator.execute(
                machine=machine,
                prompt_values=prompt_values.get(generator.name, {}),
                no_sandbox=no_sandbox,
            )


PromptFunc = Callable[[Generator], dict[str, str]]
"""Type for a function that collects prompt values for a generator.

The function receives a Generator and should return a dictionary mapping
prompt names to their values. This allows for custom prompt collection
strategies (e.g., interactive CLI, GUI, or programmatic).
"""


@API.register
def run_generators(
    machine: Machine,
    generators: GeneratorKey
    | list[GeneratorKey]
    | Literal["all", "minimal"] = "minimal",
    prompt_values: dict[str, dict[str, str]] | PromptFunc = lambda g: g.ask_prompts(),
    no_sandbox: bool = False,
) -> None:
    """Run the specified generators for a machine.
    Args:
        machine: The machine to run generators for.
        generators: Can be:
            - GeneratorKey: Single generator to run (ensuring dependencies are met)
            - list[GeneratorKey]: Specific generators to run exactly as provided.
                Dependency generators are not added automatically in this case.
                The caller must ensure that all dependencies are included.
            - "all": Run all generators (full closure)
            - "minimal": Run only missing generators (minimal closure) (default)
        prompt_values: A dictionary mapping generator names to their prompt values,
            or a function that returns prompt values for a generator.
        no_sandbox: Whether to disable sandboxing when executing the generator.
    Raises:
        ClanError: If the machine or generator is not found, or if there are issues with
        executing the generator.
    """

    if generators == "all":
        generator_objects = get_generators(machine, full_closure=True)
    elif generators == "minimal":
        generator_objects = get_generators(machine, full_closure=False)
    elif isinstance(generators, GeneratorKey):
        # Single generator - compute minimal closure for it
        generator_objects = get_generators(
            machine, full_closure=False, generator_name=generators.name
        )
    elif isinstance(generators, list):
        if len(generators) == 0:
            return
        generator_keys = set(generators)
        all_generators = get_generators(machine, full_closure=True)
        generator_objects = [g for g in all_generators if g.key in generator_keys]
    else:
        msg = f"Invalid generators argument: {generators}. Must be 'all', 'minimal', GeneratorKey, or a list of GeneratorKey"
        raise ValueError(msg)

    # If prompt function provided, ask all prompts
    # TODO: make this more lazy and ask for every generator on execution
    if callable(prompt_values):
        prompt_values = {
            generator.name: prompt_values(generator) for generator in generator_objects
        }
    _generate_vars_for_machine(
        machine=machine,
        generators=generator_objects,
        prompt_values=prompt_values,
        no_sandbox=no_sandbox,
    )


def generate_vars(
    machines: list["Machine"],
    generator_name: str | None = None,
    regenerate: bool = False,
    no_sandbox: bool = False,
) -> None:
    for machine in machines:
        errors = []
        try:
            generators: GeneratorKey | Literal["all", "minimal"]
            if generator_name:
                generators = GeneratorKey(machine=machine.name, name=generator_name)
            else:
                generators = "all" if regenerate else "minimal"

            run_generators(
                machine,
                generators=generators,
                no_sandbox=no_sandbox,
            )
            machine.info("All vars are up to date")
        except Exception as exc:
            errors += [(machine, exc)]
        if len(errors) == 1:
            raise errors[0][1]
        if len(errors) > 1:
            msg = f"Failed to generate vars for {len(errors)} hosts:"
            for machine, error in errors:
                msg += f"\n{machine}: {error}"
            raise ClanError(msg) from errors[0][1]


def generate_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machines: list[Machine] = list(list_full_machines(flake).values())

    if len(args.machines) > 0:
        machines = list(
            filter(
                lambda m: m.name in args.machines,
                machines,
            )
        )

    # prefetch all vars
    config = nix_config()
    system = config["system"]
    machine_names = [machine.name for machine in machines]
    # test
    flake.precache(
        [
            f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.generators.*.validationHash",
        ]
    )
    generate_vars(
        machines,
        args.generator,
        args.regenerate,
        no_sandbox=args.no_sandbox,
    )


def register_generate_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machines",
        type=str,
        help="machine to generate facts for. if empty, generate facts for all machines",
        nargs="*",
        default=[],
    )
    add_dynamic_completer(machines_parser, complete_machines)

    service_parser = parser.add_argument(
        "--generator",
        "-g",
        type=str,
        help="execute only the specified generator. If unset, execute all generators",
        default=None,
    )
    add_dynamic_completer(service_parser, complete_services_for_machine)

    parser.add_argument(
        "--regenerate",
        "-r",
        action=argparse.BooleanOptionalAction,
        help="whether to regenerate facts for the specified machine",
        default=None,
    )

    parser.add_argument(
        "--no-sandbox",
        action="store_true",
        help="disable sandboxing when executing the generator. WARNING: potentially executing untrusted code from external clan modules",
        default=False,
    )

    parser.add_argument(
        "--fake-prompts",
        action="store_true",
        help="automatically fill prompt responses for testing (unsafe)",
        default=False,
    )

    parser.set_defaults(func=generate_command)
