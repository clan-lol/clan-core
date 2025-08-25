from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from clan_lib.machines import machines
    from clan_lib.ssh.host import Host


class SecretStoreBase(ABC):
    @abstractmethod
    def __init__(self, machine: machines.Machine) -> None:
        pass

    @abstractmethod
    def set(
        self,
        service: str,
        name: str,
        value: bytes,
        groups: list[str],
    ) -> Path | None:
        pass

    @abstractmethod
    def get(self, service: str, name: str) -> bytes:
        pass

    @abstractmethod
    def exists(self, service: str, name: str) -> bool:
        pass

    def needs_upload(self, host: Host) -> bool:
        del host  # Unused but kept for API compatibility
        return True

    @abstractmethod
    def upload(self, output_dir: Path) -> None:
        pass
