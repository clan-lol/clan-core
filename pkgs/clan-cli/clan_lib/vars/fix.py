import logging

from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.vars.generator import get_machine_generators

log = logging.getLogger(__name__)


def fix_vars(machine: Machine, generator_name: str | None = None) -> None:
    # Resolve generators against every machine in the clan, not just the one
    # being fixed: a shared generator's `machines` must hold all machines that
    # declare it, otherwise the stores re-key shared deployed secrets to a
    # single machine (see test_age_fix_keeps_all_recipients_on_shared_deployed_secret).
    all_machines = list(machine.flake.list_machines())
    all_generators = get_machine_generators(all_machines, machine.flake)
    generators = [g for g in all_generators if machine.name in g.machines]
    if generator_name:
        for generator in generators:
            if generator_name == generator.name:
                generators = [generator]
                break
        else:
            err_msg = (
                f"Generator '{generator_name}' not found in machine {machine.name}"
            )
            raise ClanError(err_msg)

    machine.public_vars_store.fix(machine.name, generators=generators)
    machine.secret_vars_store.fix(machine.name, generators=generators)
