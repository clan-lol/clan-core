import logging
from pathlib import Path

from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.actions import list_machines
from clan_lib.vars.generator import get_machine_generators

log = logging.getLogger(__name__)


def export_vars(flake: Flake, output_dir: Path) -> None:
    """Dump all clan vars to a folder, grouped by placement.

    Layout::

        <output_dir>/
          per-machine/<machine>/<generator>/<file>
          shared/<generator>/<file>
          per-export/<exports_key>/<generator>/<file>

    The structure mirrors :meth:`Placement.rel_prefix` so it stays in sync
    with the on-disk vars layout and is naturally extensible to flake-level
    generators (``PerExport``).
    """
    if output_dir.exists():
        msg = f"Output directory {output_dir} already exists"
        raise ClanError(msg)

    machines = list_machines(flake)
    if not machines:
        log.info("No machines found in clan")
        return

    # get_machine_generators deduplicates shared generators across machines
    generators = get_machine_generators(machines, flake)

    exported = 0
    skipped = 0

    for generator in generators:
        gen_dir = output_dir / generator.key.placement.rel_prefix() / generator.name
        for var in generator.files:
            if not var.exists:
                log.warning(f"Skipping {generator.key}/{var.name}: not generated yet")
                skipped += 1
                continue

            var_path = gen_dir / var.name
            var_path.parent.mkdir(parents=True, exist_ok=True)
            var_path.write_bytes(var.value)
            exported += 1

    log.info(f"Exported {exported} vars ({skipped} skipped)")
