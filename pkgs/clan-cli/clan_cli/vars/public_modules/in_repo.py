import shutil
from collections.abc import Iterable
from pathlib import Path

from clan_cli.errors import ClanError
from clan_cli.machines.machines import Machine
from clan_cli.ssh.host import Host
from clan_cli.vars._types import StoreBase
from clan_cli.vars.generate import Generator, Var


class FactStore(StoreBase):
    @property
    def is_secret_store(self) -> bool:
        return False

    def __init__(self, machine: Machine) -> None:
        self.machine = machine
        self.works_remotely = False

    @property
    def store_name(self) -> str:
        return "in_repo"

    def _set(
        self,
        generator: Generator,
        var: Var,
        value: bytes,
    ) -> Path | None:
        if not self.machine.flake.is_local:
            msg = f"in_flake fact storage is only supported for local flakes: {self.machine.flake}"
            raise ClanError(msg)
        folder = self.directory(generator, var.name)
        file_path = folder / "value"
        if folder.exists():
            if not file_path.exists():
                # another backend has used that folder before -> error out
                self.backend_collision_error(folder)
            shutil.rmtree(folder)
        # re-create directory
        folder.mkdir(parents=True, exist_ok=True)
        file_path.touch()
        file_path.write_bytes(value)
        return file_path

    # get a single fact
    def get(self, generator: Generator, name: str) -> bytes:
        return (self.directory(generator, name) / "value").read_bytes()

    def exists(self, generator: Generator, name: str) -> bool:
        return (self.directory(generator, name) / "value").exists()

    def delete(self, generator: Generator, name: str) -> Iterable[Path]:
        fact_folder = self.directory(generator, name)
        fact_file = fact_folder / "value"
        fact_file.unlink()
        empty = None
        if next(fact_folder.iterdir(), empty) is not empty:
            return [fact_file]
        fact_folder.rmdir()
        return [fact_folder]

    def delete_store(self) -> Iterable[Path]:
        flake_root = Path(self.machine.flake_dir)
        store_folder = flake_root / "vars/per-machine" / self.machine.name
        if not store_folder.exists():
            return []
        shutil.rmtree(store_folder)
        return [store_folder]

    def populate_dir(self, output_dir: Path, phases: list[str]) -> None:
        msg = "populate_dir is not implemented for public vars stores"
        raise NotImplementedError(msg)

    def upload(self, host: Host, phases: list[str]) -> None:
        msg = "upload is not implemented for public vars stores"
        raise NotImplementedError(msg)
