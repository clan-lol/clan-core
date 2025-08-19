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
        if generator.machine is None:
            if generator.share:
                # Shared generators don't need a machine for most operations
                # but some operations (like SOPS key management) might still need one
                # This is a temporary workaround - we should handle this better
                msg = f"Shared generator '{generator.name}' requires a machine context for this operation"
                raise ClanError(msg)
            msg = f"Generator '{generator.name}' has no machine associated"
            raise ClanError(msg)
        return generator.machine

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
    ) -> Path | None:
        """
        override this method to implement the actual creation of the file
        """

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
        """
        Check the health of the store for the given machine and generators.

        This method detects any issues or inconsistencies in the store that may
        require fixing (e.g., outdated encryption keys, missing permissions).

        Args:
            machine: The name of the machine to check
            generators: List of generators to check. If None, checks all generators for the machine
            file_name: Optional specific file to check. If provided, only checks that file

        Returns:
            str | None: An error message describing issues found, or None if everything is healthy
        """
        return None

    def fix(
        self,
        machine: str,
        generators: list["Generator"] | None = None,
        file_name: str | None = None,
    ) -> None:
        """
        Fix any issues with the store for the given machine and generators.

        This method is intended to repair or update the store when inconsistencies
        are detected (e.g., re-encrypting secrets with new keys, fixing permissions).

        Args:
            machine: The name of the machine to fix vars for
            generators: List of generators to fix. If None, fixes all generators for the machine
            file_name: Optional specific file to fix. If provided, only fixes that file

        Returns:
            None
        """
        return

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
        is_migration: bool = False,
    ) -> Path | None:
        from clan_lib.machines.machines import Machine

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
        new_file = self._set(generator, var, value)
        action_str = "Migrated" if is_migration else "Updated"
        log_info: Callable
        if generator.machine is None:
            log_info = log.info
        else:
            machine = Machine(name=generator.machine, flake=self.flake)
            log_info = machine.info
        if self.is_secret_store:
            log.info(f"{action_str} secret var {generator.name}/{var.name}\n")
        else:
            if value != old_val:
                msg = f"{action_str} var {generator.name}/{var.name}"
                if not is_migration:
                    msg += f"\n  old: {old_val_str}\n  new: {string_repr(value)}"
                log_info(msg)
            else:
                log_info(
                    f"Var {generator.name}/{var.name} remains unchanged: {old_val_str}"
                )
        return new_file

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
        """
        Return the invalidation hash that indicates if a generator needs to be re-run
        due to a change in its definition
        """
        hash_file = self.directory(generator, ".validation-hash")
        if not hash_file.exists():
            return None
        return hash_file.read_text().strip()

    def set_validation(self, generator: "Generator", hash_str: str) -> Path:
        """
        Store the invalidation hash that indicates if a generator needs to be re-run
        """
        hash_file = self.directory(generator, ".validation-hash")
        hash_file.parent.mkdir(parents=True, exist_ok=True)
        hash_file.write_text(hash_str)
        return hash_file

    def hash_is_valid(self, generator: "Generator") -> bool:
        """
        Check if the invalidation hash is up to date
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
    def upload(self, machine: str, host: Host, phases: list[str]) -> None:
        pass
