from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from clan_lib.errors import ClanError

if TYPE_CHECKING:
    from ._types import StoreBase
    from .generator import Generator


@dataclass
class Var:
    id: str
    name: str
    secret: bool = True
    deploy: bool = False
    owner: str = "root"
    group: str = "root"
    mode: int = 0o400
    needed_for: str = "services"

    # TODO: those shouldn't be set here
    _store: "StoreBase | None" = None
    _generator: "Generator | None" = None

    def store(self, store: "StoreBase") -> None:
        self._store = store

    def generator(self, generator: "Generator") -> None:
        self._generator = generator

    @property
    def value(self) -> bytes:
        if self._store is None:
            msg = "Store cannot be None"
            raise ClanError(msg)
        if self._generator is None:
            msg = "Generator cannot be None"
            raise ClanError(msg)
        if not self._store.exists(self._generator, self.name):
            msg = f"Var {self.id} has not been generated yet"
            raise ValueError(msg)
        # try decode the value or return <binary blob>
        return self._store.get(self._generator, self.name)

    @property
    def printable_value(self) -> str:
        try:
            return self.value.decode()
        except UnicodeDecodeError:
            return "<binary blob>"

    def set(self, value: bytes, machine: str) -> list[Path]:
        if self._store is None:
            msg = "Store cannot be None"
            raise ClanError(msg)
        if self._generator is None:
            msg = "Generator cannot be None"
            raise ClanError(msg)
        return self._store.set(self._generator, self, value, machine)

    @property
    def exists(self) -> bool:
        if self._store is None:
            msg = "Store cannot be None"
            raise ClanError(msg)
        if self._generator is None:
            msg = "Generator cannot be None"
            raise ClanError(msg)
        return self._store.exists(self._generator, self.name)

    def __str__(self) -> str:
        if self._store is None or self._generator is None:
            return f"{self.id}: <not initialized>"

        # TODO: we don't want __str__ with side effects, this should be a separate method
        if self._store.exists(self._generator, self.name):
            if self.secret:
                return f"{self.id}: ********"
            return f"{self.id}: {self.printable_value}"
        return f"{self.id}: <not set>"
