import logging
from pathlib import Path

from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.machines.actions import list_machines
from clan_lib.vars._types import VALIDATION_HASH_NAME
from clan_lib.vars.generator import get_machine_generators

log = logging.getLogger(__name__)

# The dump holds decrypted secrets: keep it readable by the owner only.
DIR_MODE = 0o700
FILE_MODE = 0o600


def _private_dir(base: Path, rel: Path) -> Path:
    """Create ``base/rel``, giving every level mode 0700."""
    path = base
    path.mkdir(mode=DIR_MODE, exist_ok=True)
    for part in rel.parts:
        path = path / part
        path.mkdir(mode=DIR_MODE, exist_ok=True)
    return path


def export_vars(flake: Flake, output_dir: Path) -> None:
    """Dump all clan vars to a folder, grouped by placement.

    Layout::

        <output_dir>/
          per-machine/<machine>/<generator>/{<file>,.validation-hash}
          shared/<generator>/{<file>,.validation-hash}
          per-export/<exports_key>/<generator>/{<file>,.validation-hash}

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
        gen_rel = generator.key.placement.rel_prefix() / generator.name
        for var in generator.files:
            if not var.exists:
                log.warning(f"Skipping {generator.key}/{var.name}: not generated yet")
                skipped += 1
                continue

            var_path = _private_dir(output_dir, gen_rel) / var.name
            var_path.touch(mode=FILE_MODE, exist_ok=False)
            var_path.write_bytes(var.value)
            exported += 1

        # Carry the invalidation hash along, otherwise the next
        # 'clan vars generate' after an import regenerates everything and
        # overwrites the restored values.
        validation = generator.stored_validation()
        if validation is not None:
            hash_path = _private_dir(output_dir, gen_rel) / VALIDATION_HASH_NAME
            hash_path.touch(mode=FILE_MODE, exist_ok=False)
            hash_path.write_text(validation)

    log.info(f"Exported {exported} vars ({skipped} skipped)")
