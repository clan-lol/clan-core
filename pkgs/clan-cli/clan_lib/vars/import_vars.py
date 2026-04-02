import logging
from pathlib import Path

from clan_lib.flake import Flake
from clan_lib.machines.actions import list_machines
from clan_lib.machines.machines import Machine
from clan_lib.vars.list import get_machine_vars
from clan_lib.vars.set import set_var

log = logging.getLogger(__name__)


def import_vars(flake: Flake, input_dir: Path) -> None:
    machines = list_machines(flake)

    imported = 0
    skipped = 0

    for machine_name in machines:
        machine = Machine(name=machine_name, flake=flake)
        for var in get_machine_vars(machine):
            var_path = input_dir / machine_name / var.id
            if not var_path.exists():
                log.warning(f"Skipping {machine_name}/{var.id}: not found in dump")
                skipped += 1
                continue

            set_var(machine, var, var_path.read_bytes(), flake)
            imported += 1

    log.info(f"Imported {imported} vars ({skipped} skipped)")
