import logging
from pathlib import Path

from clan_lib.flake import Flake
from clan_lib.git import commit_files
from clan_lib.machines.actions import list_machines
from clan_lib.machines.machines import Machine
from clan_lib.vars._types import VALIDATION_HASH_NAME
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
        gen_imported = 0
        for var in generator.files:
            var_path = gen_dir / var.name
            if not var_path.exists():
                log.warning(f"Skipping {generator.key}/{var.name}: not found in dump")
                skipped += 1
                continue

            set_var(machine, var, var_path.read_bytes(), flake)
            gen_imported += 1

        imported += gen_imported

        # Restore the invalidation hash, otherwise the generator counts as
        # outdated and the next 'clan vars generate' overwrites what we just
        # imported.
        hash_path = gen_dir / VALIDATION_HASH_NAME
        if gen_imported and hash_path.exists():
            commit_files(
                generator.store_validation(hash_path.read_text().strip()),
                machine.flake_dir,
                f"vars: restore validation hash for {generator.key}",
            )

    log.info(f"Imported {imported} vars ({skipped} skipped)")
