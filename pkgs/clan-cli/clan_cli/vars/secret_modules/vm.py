import shutil
from collections.abc import Iterable
from pathlib import Path

from clan_cli.dirs import vm_state_dir
from clan_cli.machines.machines import Machine
from clan_cli.vars._types import StoreBase
from clan_cli.vars.generate import Generator, Var


class SecretStore(StoreBase):
    @property
    def is_secret_store(self) -> bool:
        return True

    def __init__(self, machine: Machine) -> None:
        self.machine = machine
        self.dir = vm_state_dir(machine.flake.identifier, machine.name) / "secrets"
        self.dir.mkdir(parents=True, exist_ok=True)

    @property
    def store_name(self) -> str:
        return "vm"

    def _set(
        self,
        generator: Generator,
        var: Var,
        value: bytes,
    ) -> Path | None:
        secret_file = self.dir / generator.name / var.name
        secret_file.parent.mkdir(parents=True, exist_ok=True)
        secret_file.write_bytes(value)
        return None  # we manage the files outside of the git repo

    def exists(self, generator: "Generator", name: str) -> bool:
        return (self.dir / generator.name / name).exists()

    def get(self, generator: Generator, name: str) -> bytes:
        secret_file = self.dir / generator.name / name
        return secret_file.read_bytes()

    def delete(self, generator: Generator, name: str) -> Iterable[Path]:
        secret_dir = self.dir / generator.name
        secret_file = secret_dir / name
        secret_file.unlink()
        empty = None
        if next(secret_dir.iterdir(), empty) is empty:
            secret_dir.rmdir()
        return [secret_file]

    def delete_store(self) -> Iterable[Path]:
        if not self.dir.exists():
            return []
        shutil.rmtree(self.dir)
        return [self.dir]

    def populate_dir(self, output_dir: Path, phases: list[str]) -> None:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        shutil.copytree(self.dir, output_dir)

    def upload(self, phases: list[str]) -> None:
        msg = "Cannot upload secrets to VMs"
        raise NotImplementedError(msg)
