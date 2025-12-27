import logging
import shutil
from collections.abc import Iterable
from pathlib import Path

from clan_lib.dirs import vm_state_dir
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.ssh.host import Host
from clan_lib.vars._types import StoreBase
from clan_lib.vars.generator import Generator, Var

log = logging.getLogger(__name__)


class VarsStore(StoreBase):
    @property
    def is_secret_store(self) -> bool:
        return False

    def __init__(self, flake: Flake) -> None:
        super().__init__(flake)
        self.works_remotely = False

    @property
    def store_name(self) -> str:
        return "vm"

    def get_dir(self, machine: str) -> Path:
        """Get the directory for a given machine."""
        vars_dir = vm_state_dir(self.flake.identifier, machine) / "vars"
        log.debug(
            f"vars store using dir {vars_dir}",
            extra={"command_prefix": machine},
        )
        return vars_dir

    def exists(self, generator: Generator, name: str) -> bool:
        machine = self.get_machine(generator)
        fact_path = self.get_dir(machine) / generator.name / name
        return fact_path.exists()

    def _set(
        self,
        generator: Generator,
        var: Var,
        value: bytes,
        machine: str,
    ) -> Path | None:
        fact_path = self.get_dir(machine) / generator.name / var.name
        fact_path.parent.mkdir(parents=True, exist_ok=True)
        fact_path.write_bytes(value)
        return None

    # get a single fact
    def get(self, generator: Generator, name: str) -> bytes:
        machine = self.get_machine(generator)
        fact_path = self.get_dir(machine) / generator.name / name
        if fact_path.exists():
            return fact_path.read_bytes()
        msg = f"Fact {name} for service {generator.name} not found"
        raise ClanError(msg)

    def delete(self, generator: Generator, name: str) -> Iterable[Path]:
        machine = self.get_machine(generator)
        fact_dir = self.get_dir(machine) / generator.name
        fact_file = fact_dir / name
        fact_file.unlink()
        empty = None
        if next(fact_dir.iterdir(), empty) is empty:
            fact_dir.rmdir()
        return [fact_file]

    def delete_store(self, machine: str) -> Iterable[Path]:
        vars_dir = self.get_dir(machine)
        if not vars_dir.exists():
            return []
        shutil.rmtree(vars_dir)
        return [vars_dir]

    def populate_dir(self, machine: str, output_dir: Path, phases: list[str]) -> None:
        msg = "populate_dir is not implemented for public vars stores"
        raise NotImplementedError(msg)

    def get_upload_directory(self, machine: str) -> str:
        del machine  # Unused
        msg = "Public var stores do not have upload directories"
        raise NotImplementedError(msg)

    def upload(self, machine: str, host: Host, phases: list[str]) -> None:
        msg = "upload is not implemented for public vars stores"
        raise NotImplementedError(msg)
