import logging

from clan_lib.machines.machines import Machine
from clan_lib.vars.generator import Generator, Var

log = logging.getLogger(__name__)


def get_machine_vars(machine: Machine) -> list[Var]:
    """Get all vars for a machine.

    Args:
        machine: The machine to get vars for.

    Returns:
        List of all vars for the machine with their current values and metadata.

    """
    # TODO: We dont have machine level store / this granularity yet
    # We should move the store definition to the flake, as there can be only one store per clan

    all_vars = []

    # Only load the specific machine's generators for better performance
    generators = Generator.get_machine_generators([machine.name], machine.flake)

    for generator in generators:
        for var in generator.files:
            if var.secret:
                var.store(machine.secret_vars_store)
            else:
                var.store(machine.public_vars_store)
            var.generator(generator)
            all_vars.append(var)
    return all_vars


def stringify_all_vars(machine: Machine) -> str:
    all_vars = get_machine_vars(machine)
    return "\n".join([str(var) for var in all_vars])
