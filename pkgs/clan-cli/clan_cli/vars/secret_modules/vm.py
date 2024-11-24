import shutil
from pathlib import Path

from clan_cli.dirs import vm_state_dir
from clan_cli.machines.machines import Machine

from . import SecretStoreBase


class SecretStore(SecretStoreBase):
    def __init__(self, machine: Machine) -> None:
        self.machine = machine
        self.dir = vm_state_dir(machine.flake, machine.name) / "secrets"
        self.dir.mkdir(parents=True, exist_ok=True)

    @property
    def store_name(self) -> str:
        return "vm"

    def _set(
        self,
        service: str,
        name: str,
        value: bytes,
        shared: bool = False,
        deployed: bool = True,
    ) -> Path | None:
        secret_file = self.dir / service / name
        secret_file.parent.mkdir(parents=True, exist_ok=True)
        secret_file.write_bytes(value)
        return None  # we manage the files outside of the git repo

    def get(self, service: str, name: str, shared: bool = False) -> bytes:
        secret_file = self.dir / service / name
        return secret_file.read_bytes()

    def upload(self, output_dir: Path) -> None:
        if output_dir.exists():
            shutil.rmtree(output_dir)
        shutil.copytree(self.dir, output_dir)
