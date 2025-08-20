import shutil
from collections.abc import Iterable
from pathlib import Path

from clan_cli.vars._types import StoreBase
from clan_cli.vars.generator import Generator, Var
from clan_lib.dirs import vm_state_dir
from clan_lib.flake import Flake
from clan_lib.ssh.host import Host


class SecretStore(StoreBase):
    @property
    def is_secret_store(self) -> bool:
        return True

    def __init__(self, flake: Flake) -> None:
        super().__init__(flake)

    @property
    def store_name(self) -> str:
        return "vm"

    def get_dir(self, machine: str) -> Path:
        """Get the directory for a given machine, creating it if needed."""
        vars_dir = vm_state_dir(self.flake.identifier, machine) / "secrets"
        vars_dir.mkdir(parents=True, exist_ok=True)
        return vars_dir

    def _set(
        self,
        generator: Generator,
        var: Var,
        value: bytes,
    ) -> Path | None:
        machine = self.get_machine(generator)
        secret_file = self.get_dir(machine) / generator.name / var.name
        secret_file.parent.mkdir(parents=True, exist_ok=True)
        secret_file.write_bytes(value)
        return None  # we manage the files outside of the git repo

    def exists(self, generator: "Generator", name: str) -> bool:
        machine = self.get_machine(generator)
        return (self.get_dir(machine) / generator.name / name).exists()

    def get(self, generator: Generator, name: str) -> bytes:
        machine = self.get_machine(generator)
        secret_file = self.get_dir(machine) / generator.name / name
        return secret_file.read_bytes()

    def delete(self, generator: Generator, name: str) -> Iterable[Path]:
        machine = self.get_machine(generator)
        secret_dir = self.get_dir(machine) / generator.name
        secret_file = secret_dir / name
        secret_file.unlink()
        empty = None
        if next(secret_dir.iterdir(), empty) is empty:
            secret_dir.rmdir()
        return [secret_file]

    def delete_store(self, machine: str) -> Iterable[Path]:
        vars_dir = self.get_dir(machine)
        if not vars_dir.exists():
            return []
        shutil.rmtree(vars_dir)
        return [vars_dir]

    def populate_dir(self, machine: str, output_dir: Path, phases: list[str]) -> None:
        del phases  # Unused but kept for API compatibility
        vars_dir = self.get_dir(machine)
        if output_dir.exists():
            shutil.rmtree(output_dir)
        shutil.copytree(vars_dir, output_dir)

    def upload(self, machine: str, host: Host, phases: list[str]) -> None:
        msg = "Cannot upload secrets to VMs"
        raise NotImplementedError(msg)
