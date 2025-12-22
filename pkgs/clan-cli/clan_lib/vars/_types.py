import dataclasses
import logging
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.ssh.host import Host

if TYPE_CHECKING:
    from .generator import Generator, Var

log = logging.getLogger(__name__)


def string_repr(value: bytes) -> str:
    try:
        return value.decode()
    except UnicodeDecodeError:
        return "<binary blob>"


@dataclass
class GeneratorUpdate:
    generator: str
    prompt_values: dict[str, str]


class StoreBase(ABC):
    def __init__(self, flake: Flake) -> None:
        self.flake = flake

    @property
    @abstractmethod
    def store_name(self) -> str:
        pass

    def get_machine(self, generator: "Generator") -> str:
        """Get machine name from generator, asserting it's not None for now."""
        if generator.share:
            return "__shared"
        if not generator.machines:
            msg = f"Generator '{generator.name}' has no machine associated"
            raise ClanError(msg)
        if len(generator.machines) != 1:
            msg = f"Generator '{generator.name}' has {len(generator.machines)} machines, expected exactly 1"
            raise ClanError(msg)
        return generator.machines[0]

    # get a single fact
    @abstractmethod
    def get(self, generator: "Generator", name: str) -> bytes:
        pass

    @abstractmethod
    def _set(
        self,
        generator: "Generator",
        var: "Var",
        value: bytes,
        machine: str,
    ) -> Path | None:
        """Override this method to implement the actual creation of the file"""

    @abstractmethod
    def exists(self, generator: "Generator", name: str) -> bool:
        pass

    @property
    @abstractmethod
    def is_secret_store(self) -> bool:
        pass

    def health_check(
        self,
        machine: str,
        generators: list["Generator"] | None = None,
        file_name: str | None = None,
    ) -> str | None:
        """Check the health of the store for the given machine and generators.

        This method detects any issues or inconsistencies in the store that may
        require fixing (e.g., outdated encryption keys, missing permissions).

        Args:
            machine: The name of the machine to check
            generators: List of generators to check. If None, checks all generators for the machine
            file_name: Optional specific file to check. If provided, only checks that file

        Returns:
            str | None: An error message describing issues found, or None if everything is healthy

        """
        del machine, generators, file_name  # Unused but kept for API compatibility
        return None

    def fix(
        self,
        machine: str,
        generators: list["Generator"] | None = None,
        file_name: str | None = None,
    ) -> None:
        """Fix any issues with the store for the given machine and generators.

        This method is intended to repair or update the store when inconsistencies
        are detected (e.g., re-encrypting secrets with new keys, fixing permissions).

        Args:
            machine: The name of the machine to fix vars for
            generators: List of generators to fix. If None, fixes all generators for the machine
            file_name: Optional specific file to fix. If provided, only fixes that file

        Returns:
            None

        """
        del machine, generators, file_name  # Unused but kept for API compatibility

    def backend_collision_error(self, folder: Path) -> None:
        msg = (
            f"Var folder {folder} exists but doesn't look like a {self.store_name} secret.\n"
            "Potentially a leftover from another backend. Please delete it manually."
        )
        raise ClanError(msg)

    def rel_dir(self, generator: "Generator", var_name: str) -> Path:
        if generator.share:
            return Path("shared") / generator.name / var_name
        machine = self.get_machine(generator)
        return Path("per-machine") / machine / generator.name / var_name

    def directory(self, generator: "Generator", var_name: str) -> Path:
        return self.flake.path / "vars" / self.rel_dir(generator, var_name)

    def set(
        self,
        generator: "Generator",
        var: "Var",
        value: bytes,
        machine: str,
        is_migration: bool = False,
    ) -> list[Path]:
        changed_files: list[Path] = []

        # if generator was switched from shared to per-machine or vice versa,
        # remove the old var first
        prev_generator = dataclasses.replace(
            generator,
            share=not generator.share,
            machines=[] if not generator.share else [machine],
        )
        if self.exists(prev_generator, var.name):
            changed_files += self.delete(prev_generator, var.name)

        if self.exists(generator, var.name):
            if self.is_secret_store:
                old_val = None
                old_val_str = "********"
            else:
                old_val = self.get(generator, var.name)
                old_val_str = string_repr(old_val)
        else:
            old_val = None
            old_val_str = "<not set>"
        new_file = self._set(generator, var, value, machine)
        action_str = "Migrated" if is_migration else "Updated"
        log_info: Callable
        if generator.share:
            log_info = log.info
        else:
            from clan_lib.machines.machines import Machine  # noqa: PLC0415

            machine_obj = Machine(name=generator.machines[0], flake=self.flake)
            log_info = machine_obj.info
        machines_str = f" for machines: {', '.join(generator.machines)}"
        if self.is_secret_store:
            log.info(
                f"{action_str} secret var {generator.name}/{var.name}{machines_str}\n"
            )
        elif value != old_val:
            msg = f"{action_str} var {generator.name}/{var.name}{machines_str}"
            if not is_migration:
                msg += f"\n  old: {old_val_str}\n  new: {string_repr(value)}"
            log_info(msg)
        else:
            log_info(
                f"Var {generator.name}/{var.name}{machines_str} remains unchanged: {old_val_str}",
            )
        changed_files += [new_file] if new_file else []
        return changed_files

    @abstractmethod
    def delete(self, generator: "Generator", name: str) -> Iterable[Path]:
        """Remove a var from the store.

        :return: An iterable of affected paths in the git repository. This
          may be empty if the store is outside of the repository.
        """

    @abstractmethod
    def delete_store(self, machine: str) -> Iterable[Path]:
        """Delete the store (all vars) for this machine.

        .. note::

           This does not make the distinction between public and private vars.
           Since the public and private store of a machine can be co-located
           under the same directory, this method's implementation has to be
           idempotent.

        :return: An iterable of affected paths in the git repository. This
          may be empty if the store was outside of the repository.
        """

    def get_validation(self, generator: "Generator") -> str | None:
        """Return the invalidation hash that indicates if a generator needs to be re-run
        due to a change in its definition
        """
        hash_file = self.directory(generator, ".validation-hash")
        if not hash_file.exists():
            return None
        return hash_file.read_text().strip()

    def set_validation(
        self, generator: "Generator", hash_str: str | None
    ) -> list[Path]:
        # """Store the invalidation hash that indicates if a generator needs to be re-run"""
        """Store the invalidation hash that indicates if a generator needs to be re-run

        Args:
            generator (Generator): The generator for which to store the hash
            hash_str (str | None): The hash string to store. If None, the existing
                hash file will be deleted.

        Returns:
            pathlib.Path: The path to the hash file

        """
        hash_file = self.directory(generator, ".validation-hash")
        hash_file.parent.mkdir(parents=True, exist_ok=True)
        if hash_str is None:
            if hash_file.exists():
                hash_file.unlink()
                return [hash_file]
            return []
        hash_file.write_text(hash_str)
        return [hash_file]

    def hash_is_valid(self, generator: "Generator") -> bool:
        """Check if the invalidation hash is up to date
        If the hash is not set in nix and hasn't been stored before, it is considered valid
            -> this provides backward and forward compatibility
        """
        stored_hash = self.get_validation(generator)
        target_hash = generator.validation()
        # if the hash is neither set in nix nor on disk, it is considered valid (provides backwards compat)
        if target_hash is None and stored_hash is None:
            return True
        return stored_hash == target_hash

    @abstractmethod
    def populate_dir(self, machine: str, output_dir: Path, phases: list[str]) -> None:
        pass

    @abstractmethod
    def get_upload_directory(self, machine: str) -> str:
        """Return the target directory path where secrets should be uploaded.

        This is the absolute path on the target machine where the secret store
        expects files to be placed (e.g., /var/lib/sops-nix for sops backend).
        Used by install.py to construct the correct directory structure for
        nixos-anywhere's --extra-files.
        """

    @abstractmethod
    def upload(self, machine: str, host: Host, phases: list[str]) -> None:
        pass
