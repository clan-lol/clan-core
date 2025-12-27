import logging

from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.vars.generator import Generator

log = logging.getLogger(__name__)


def fix_vars(machine: Machine, generator_name: None | str = None) -> None:
    generators = Generator.get_machine_generators([machine.name], machine.flake)
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
