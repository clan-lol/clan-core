import logging
from pathlib import Path

from clan_lib.machines.machines import Machine
from clan_lib.ssh.host import Host
from clan_lib.vars.generate import get_flake_generators
from clan_lib.vars.generator import get_machine_generators

log = logging.getLogger(__name__)


def upload_secret_vars(machine: Machine, host: Host) -> None:
    machine_generators = get_machine_generators([machine.name], machine.flake)
    flake_generators = get_flake_generators(machine.flake)
    all_generators = machine_generators + list(flake_generators.values())

    machine.secret_vars_store.upload(
        all_generators,
        machine.name,
        host,
        phases=["activation", "users", "services"],
    )


def populate_secret_vars(machine: Machine, directory: Path) -> None:
    generators = get_machine_generators([machine.name], machine.flake)
    machine.secret_vars_store.populate_dir(
        generators,
        machine.name,
        directory,
        phases=["activation", "users", "services"],
    )
