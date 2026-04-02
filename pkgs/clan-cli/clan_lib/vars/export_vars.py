import logging
from pathlib import Path

from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.actions import list_machines
from clan_lib.machines.machines import Machine
from clan_lib.vars.list import get_machine_vars

log = logging.getLogger(__name__)


def export_vars(flake: Flake, output_dir: Path) -> None:
    if output_dir.exists():
        msg = f"Output directory {output_dir} already exists"
        raise ClanError(msg)

    machines = list_machines(flake)
    if not machines:
        log.info("No machines found in clan")
        return

    exported = 0
    skipped = 0

    for machine_name in machines:
        machine = Machine(name=machine_name, flake=flake)
        for var in get_machine_vars(machine):
            if not var.exists:
                log.warning(f"Skipping {machine_name}/{var.id}: not generated yet")
                skipped += 1
                continue

            var_path = output_dir / machine_name / var.id
            var_path.parent.mkdir(parents=True, exist_ok=True)
            var_path.write_bytes(var.value)
            exported += 1

    log.info(f"Exported {exported} vars ({skipped} skipped)")
