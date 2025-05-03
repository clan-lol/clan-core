import logging
from pathlib import Path
from typing import TYPE_CHECKING

from clan_cli.errors import ClanError
from clan_cli.git import commit_files

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from clan_cli.machines.machines import Machine
    from clan_cli.vars.generate import Generator


def _migration_file_exists(
    machine: "Machine",
    generator: "Generator",
    fact_name: str,
) -> bool:
    for file in generator.files:
        if file.name == fact_name:
            break
    else:
        msg = f"Could not find file {fact_name} in generator {generator.name}"
        raise ClanError(msg)

    is_secret = file.secret
    if is_secret:
        if machine.secret_facts_store.exists(generator.name, fact_name):
            return True
        machine.debug(
            f"Cannot migrate fact {fact_name} for service {generator.name}, as it does not exist in the secret fact store"
        )
    if not is_secret:
        if machine.public_facts_store.exists(generator.name, fact_name):
            return True
        machine.debug(
            f"Cannot migrate fact {fact_name} for service {generator.name}, as it does not exist in the public fact store"
        )
    return False


def _migrate_file(
    machine: "Machine",
    generator: "Generator",
    var_name: str,
    service_name: str,
    fact_name: str,
) -> list[Path]:
    for file in generator.files:
        if file.name == var_name:
            break
    else:
        msg = f"Could not find file {fact_name} in generator {generator.name}"
        raise ClanError(msg)

    paths = []

    if file.secret:
        old_value = machine.secret_facts_store.get(service_name, fact_name)
        maybe_path = machine.secret_vars_store.set(
            generator, file, old_value, is_migration=True
        )
        if maybe_path:
            paths.append(maybe_path)
    else:
        old_value = machine.public_facts_store.get(service_name, fact_name)
        maybe_path = machine.public_vars_store.set(
            generator, file, old_value, is_migration=True
        )
        if maybe_path:
            paths.append(maybe_path)

    return paths


def migrate_files(
    machine: "Machine",
    generator: "Generator",
) -> None:
    not_found = []
    files_to_commit = []
    for file in generator.files:
        if _migration_file_exists(machine, generator, file.name):
            assert generator.migrate_fact is not None
            files_to_commit += _migrate_file(
                machine, generator, file.name, generator.migrate_fact, file.name
            )
        else:
            not_found.append(file.name)
    if len(not_found) > 0:
        msg = f"Could not migrate the following files for generator {generator.name}, as no fact or secret exists with the same name: {not_found}"
        raise ClanError(msg)
    commit_files(
        files_to_commit,
        machine.flake_dir,
        f"migrated facts to vars for generator {generator.name} for machine {machine.name}",
    )


def check_can_migrate(
    machine: "Machine",
    generator: "Generator",
) -> bool:
    service_name = generator.migrate_fact
    if not service_name:
        return False
    # ensure that none of the generated vars already exist in the store
    all_files_missing = True
    all_files_present = True
    for file in generator.files:
        if file.secret:
            if machine.secret_vars_store.exists(generator, file.name):
                all_files_missing = False
            else:
                all_files_present = False
        else:
            if machine.public_vars_store.exists(generator, file.name):
                all_files_missing = False
            else:
                all_files_present = False

    if not all_files_present and not all_files_missing:
        msg = f"Cannot migrate facts for generator {generator.name} as some files already exist in the store"
        raise ClanError(msg)
    if all_files_present:
        # all files already migrated, no need to run migration again
        return False

    # ensure that all files can be migrated (exists in the corresponding fact store)
    return bool(
        all(
            _migration_file_exists(machine, generator, file.name)
            for file in generator.files
        )
    )
