import shutil
from collections.abc import Iterable, Sequence
from pathlib import Path

from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.ssh.host import Host
from clan_lib.vars._types import GeneratorId, GeneratorStore, StoreBase
from clan_lib.vars.var import Var


class VarsStore(StoreBase):
    @property
    def is_secret_store(self) -> bool:
        return False

    def __init__(self, flake: Flake) -> None:
        super().__init__(flake)
        self.works_remotely = False

    @property
    def store_name(self) -> str:
        return "in_repo"

    def _set(
        self,
        generator: GeneratorStore,
        var: Var,
        value: bytes,
        machine: str,  # noqa: ARG002
    ) -> Path | None:
        if not self.flake.is_local:
            msg = f"Storing var '{var.id}' in a flake is only supported for local flakes: {self.flake}"
            raise ClanError(msg)
        folder = self.directory(generator.key, var.name)
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
    def get(
        self,
        generator: GeneratorId,
        name: str,
    ) -> bytes:
        return (self.directory(generator, name) / "value").read_bytes()

    def exists(self, generator: GeneratorId, name: str) -> bool:
        return (self.directory(generator, name) / "value").exists()

    def delete(self, generator: GeneratorId, name: str) -> Iterable[Path]:
        fact_folder = self.directory(generator, name)
        fact_file = fact_folder / "value"
        fact_file.unlink()
        empty = None
        if next(fact_folder.iterdir(), empty) is not empty:
            return [fact_file]
        fact_folder.rmdir()
        return [fact_folder]

    def delete_store(self, machine: str) -> Iterable[Path]:
        flake_root = self.flake.path
        store_folder = flake_root / "vars/per-machine" / machine
        if not store_folder.exists():
            return []
        shutil.rmtree(store_folder)
        return [store_folder]

    def populate_dir(
        self,
        generators: Sequence[GeneratorStore],
        machine: str,
        output_dir: Path,
        phases: list[str],
    ) -> None:
        msg = "populate_dir is not implemented for public vars stores"
        raise NotImplementedError(msg)

    def get_upload_directory(self, machine: str) -> str:
        del machine  # Unused
        msg = "Public var stores do not have upload directories"
        raise NotImplementedError(msg)

    def upload(
        self,
        generators: Sequence[GeneratorStore],
        machine: str,
        host: Host,
        phases: list[str],
    ) -> None:
        msg = "upload is not implemented for public vars stores"
        raise NotImplementedError(msg)
