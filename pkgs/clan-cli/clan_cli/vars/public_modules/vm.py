import logging
import shutil
from collections.abc import Iterable
from pathlib import Path

from clan_cli.machines.machines import Machine
from clan_cli.ssh.host import Host
from clan_cli.vars._types import StoreBase
from clan_cli.vars.generate import Generator, Var
from clan_lib.dirs import vm_state_dir
from clan_lib.errors import ClanError

log = logging.getLogger(__name__)


class FactStore(StoreBase):
    @property
    def is_secret_store(self) -> bool:
        return False

    def __init__(self, machine: Machine) -> None:
        self.machine = machine
        self.works_remotely = False
        self.dir = vm_state_dir(machine.flake.identifier, machine.name) / "facts"
        machine.debug(f"FactStore initialized with dir {self.dir}")

    @property
    def store_name(self) -> str:
        return "vm"

    def exists(self, generator: Generator, name: str) -> bool:
        fact_path = self.dir / generator.name / name
        return fact_path.exists()

    def _set(
        self,
        generator: Generator,
        var: Var,
        value: bytes,
    ) -> Path | None:
        fact_path = self.dir / generator.name / var.name
        fact_path.parent.mkdir(parents=True, exist_ok=True)
        fact_path.write_bytes(value)
        return None

    # get a single fact
    def get(self, generator: Generator, name: str) -> bytes:
        fact_path = self.dir / generator.name / name
        if fact_path.exists():
            return fact_path.read_bytes()
        msg = f"Fact {name} for service {generator.name} not found"
        raise ClanError(msg)

    def delete(self, generator: Generator, name: str) -> Iterable[Path]:
        fact_dir = self.dir / generator.name
        fact_file = fact_dir / name
        fact_file.unlink()
        empty = None
        if next(fact_dir.iterdir(), empty) is empty:
            fact_dir.rmdir()
        return [fact_file]

    def delete_store(self) -> Iterable[Path]:
        if not self.dir.exists():
            return []
        shutil.rmtree(self.dir)
        return [self.dir]

    def populate_dir(self, output_dir: Path, phases: list[str]) -> None:
        msg = "populate_dir is not implemented for public vars stores"
        raise NotImplementedError(msg)

    def upload(self, host: Host, phases: list[str]) -> None:
        msg = "upload is not implemented for public vars stores"
        raise NotImplementedError(msg)
