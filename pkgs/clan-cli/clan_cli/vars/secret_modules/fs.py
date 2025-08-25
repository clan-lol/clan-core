import shutil
import tempfile
from pathlib import Path

from clan_cli.vars._types import StoreBase
from clan_cli.vars.generator import Generator, Var
from clan_lib.flake import Flake
from clan_lib.ssh.host import Host


class SecretStore(StoreBase):
    @property
    def is_secret_store(self) -> bool:
        return True

    def __init__(self, flake: Flake) -> None:
        super().__init__(flake)
        self.dir = Path(tempfile.gettempdir()) / "clan_secrets"
        self.dir.mkdir(parents=True, exist_ok=True)

    @property
    def store_name(self) -> str:
        return "fs"

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

    def populate_dir(self, machine: str, output_dir: Path, phases: list[str]) -> None:
        del machine, phases  # Unused but kept for API compatibility
        if output_dir.exists():
            shutil.rmtree(output_dir)
        shutil.copytree(self.dir, output_dir)
        shutil.rmtree(self.dir)

    def delete(self, generator: Generator, name: str) -> list[Path]:
        secret_file = self.dir / generator.name / name
        if secret_file.exists():
            secret_file.unlink()
        return []

    def delete_store(self, machine: str) -> list[Path]:
        del machine  # Unused but kept for API compatibility
        if self.dir.exists():
            shutil.rmtree(self.dir)
        return []

    def upload(self, machine: str, host: Host, phases: list[str]) -> None:
        msg = "Cannot upload secrets with FS backend"
        raise NotImplementedError(msg)
