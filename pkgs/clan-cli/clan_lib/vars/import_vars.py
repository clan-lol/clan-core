import logging
from pathlib import Path

from clan_lib.flake import Flake
from clan_lib.machines.actions import list_machines
from clan_lib.machines.machines import Machine
from clan_lib.vars.generator import get_machine_generators
from clan_lib.vars.set import set_var

log = logging.getLogger(__name__)


def import_vars(flake: Flake, input_dir: Path) -> None:
    """Restore vars previously written by :func:`export_vars`.

    Reads files laid out by placement (``per-machine/``, ``shared/``,
    ``per-export/``) and writes them back through the configured backend.
    """
    machines = list_machines(flake)
    generators = get_machine_generators(machines, flake)

    imported = 0
    skipped = 0

    for generator in generators:
        gen_dir = input_dir / generator.key.placement.rel_prefix() / generator.name
        # For shared/per-export generators, set_var still needs *a* machine
        # (used for re-encryption); pick any machine that knows this generator.
        machine_name = generator.machines[0]
        machine = Machine(name=machine_name, flake=flake)
        for var in generator.files:
            var_path = gen_dir / var.name
            if not var_path.exists():
                log.warning(f"Skipping {generator.key}/{var.name}: not found in dump")
                skipped += 1
                continue

            set_var(machine, var, var_path.read_bytes(), flake)
            imported += 1

    log.info(f"Imported {imported} vars ({skipped} skipped)")
