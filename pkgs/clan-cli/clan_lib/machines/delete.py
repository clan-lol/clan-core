import logging
import shutil
from typing import TYPE_CHECKING

from clan_cli.secrets.folders import sops_secrets_folder
from clan_cli.secrets.machines import has_machine as secrets_has_machine
from clan_cli.secrets.machines import remove_machine as secrets_machine_remove
from clan_cli.secrets.secrets import (
    list_secrets,
)

from clan_lib.api import API
from clan_lib.dirs import specific_machine_dir
from clan_lib.machines.machines import Machine
from clan_lib.persist.inventory_store import InventoryStore

if TYPE_CHECKING:
    from pathlib import Path

log = logging.getLogger(__name__)


@API.register
def delete_machine(machine: Machine) -> None:
    """Delete a machine from the clan's inventory and remove its associated files.

    Args:
        machine: The Machine instance to be deleted.

    Raises:
        ClanError: If the machine does not exist in the inventory or if there are issues with
            removing its files.

    """
    inventory_store = InventoryStore(machine.flake)
    try:
        inventory_store.delete(
            {("machines", machine.name)},
        )
    except KeyError as exc:
        # louis@(2025-03-09): test infrastructure does not seem to set the
        # inventory properly, but more importantly only one machine in my
        # personal clan ended up in the inventory for some reason, so I think
        # it makes sense to eat the exception here.
        log.warning(
            f"{machine.name} was missing or already deleted from the machines inventory: {exc}",
        )

    changed_paths: list[Path] = []

    folder = specific_machine_dir(machine)
    if folder.exists():
        changed_paths.append(folder)
        shutil.rmtree(folder)

    # louis@(2025-02-04): clean-up legacy (pre-vars) secrets:
    sops_folder = sops_secrets_folder(machine.flake.path)

    def filter_fn(secret_name: str) -> bool:
        return secret_name.startswith(f"{machine.name}-")

    for secret_name in list_secrets(machine.flake.path, filter_fn):
        secret_path = sops_folder / secret_name
        changed_paths.append(secret_path)
        shutil.rmtree(secret_path)

    changed_paths.extend(machine.public_vars_store.delete_store(machine.name))
    changed_paths.extend(machine.secret_vars_store.delete_store(machine.name))
    # Remove the machine's key, and update secrets & vars that referenced it:
    if secrets_has_machine(machine.flake.path, machine.name):
        secrets_machine_remove(machine.flake.path, machine.name)
