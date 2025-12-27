import logging
from pathlib import Path

from clan_lib.machines.machines import Machine
from clan_lib.ssh.host import Host

log = logging.getLogger(__name__)


def upload_secret_vars(machine: Machine, host: Host) -> None:
    machine.secret_vars_store.upload(
        machine.name,
        host,
        phases=["activation", "users", "services"],
    )


def populate_secret_vars(machine: Machine, directory: Path) -> None:
    machine.secret_vars_store.populate_dir(
        machine.name,
        directory,
        phases=["activation", "users", "services"],
    )
