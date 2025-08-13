import io
import logging
import subprocess
import tarfile
from collections.abc import Iterable
from pathlib import Path
from tempfile import TemporaryDirectory

from clan_cli.vars._types import StoreBase
from clan_cli.vars.generate import Generator, Var
from clan_lib.flake import Flake
from clan_lib.ssh.host import Host
from clan_lib.ssh.upload import upload

log = logging.getLogger(__name__)


class SecretStore(StoreBase):
    @property
    def is_secret_store(self) -> bool:
        return True

    def __init__(self, flake: Flake) -> None:
        super().__init__(flake)
        self.entry_prefix = "clan-vars"
        self._store_dir: Path | None = None

    @property
    def store_name(self) -> str:
        return "password_store"

    def store_dir(self, machine: str) -> Path:
        """Get the password store directory, cached per machine."""
        if not self._store_dir:
            result = self._run_pass(
                machine, "git", "rev-parse", "--show-toplevel", check=False
            )
            if result.returncode != 0:
                msg = "Password store must be a git repository"
                raise ValueError(msg)
            self._store_dir = Path(result.stdout.strip().decode())
        return self._store_dir

    def _pass_command(self, machine: str) -> str:
        out_path = self.flake.select_machine(
            machine, "config.clan.core.vars.password-store.passPackage.outPath"
        )
        main_program = (
            self.flake.select_machine(
                machine,
                "config.clan.core.vars.password-store.passPackage.?meta.?mainProgram",
            )
            .get("meta", {})
            .get("mainProgram")
        )

        if main_program:
            binary_path = Path(out_path) / "bin" / main_program
            if binary_path.exists():
                return str(binary_path)

        # Look for common password store binaries
        bin_dir = Path(out_path) / "bin"
        if bin_dir.exists():
            for binary in ["pass", "passage"]:
                binary_path = bin_dir / binary
                if binary_path.exists():
                    return str(binary_path)

            # If only one binary exists, use it
            binaries = [f for f in bin_dir.iterdir() if f.is_file()]
            if len(binaries) == 1:
                return str(binaries[0])

        msg = "Could not find password store binary in package"
        raise ValueError(msg)

    def entry_dir(self, generator: Generator, name: str) -> Path:
        return Path(self.entry_prefix) / self.rel_dir(generator, name)

    def _run_pass(
        self,
        machine: str,
        *args: str,
        input: bytes | None = None,  # noqa: A002
        check: bool = True,
    ) -> subprocess.CompletedProcess[bytes]:
        cmd = [self._pass_command(machine), *args]
        # We need bytes support here, so we can not use clan cmd.
        # If you change this to run( add bytes support to it first!
        # otherwise we mangle binary secrets (which is annoying to debug)
        return subprocess.run(
            cmd,
            input=input,
            capture_output=True,
            check=check,
        )

    def _set(
        self,
        generator: Generator,
        var: Var,
        value: bytes,
    ) -> Path | None:
        machine = self.get_machine(generator)
        pass_call = ["insert", "-m", str(self.entry_dir(generator, var.name))]
        self._run_pass(machine, *pass_call, input=value, check=True)
        return None  # we manage the files outside of the git repo

    def get(self, generator: Generator, name: str) -> bytes:
        machine = self.get_machine(generator)
        pass_name = str(self.entry_dir(generator, name))
        return self._run_pass(machine, "show", pass_name).stdout

    def exists(self, generator: Generator, name: str) -> bool:
        machine = self.get_machine(generator)
        pass_name = str(self.entry_dir(generator, name))
        # Check if the file exists with either .age or .gpg extension
        store_dir = self.store_dir(machine)
        age_file = store_dir / f"{pass_name}.age"
        gpg_file = store_dir / f"{pass_name}.gpg"
        return age_file.exists() or gpg_file.exists()

    def delete(self, generator: Generator, name: str) -> Iterable[Path]:
        machine = self.get_machine(generator)
        pass_name = str(self.entry_dir(generator, name))
        self._run_pass(machine, "rm", "--force", pass_name, check=True)
        return []

    def delete_store(self, machine: str) -> Iterable[Path]:
        machine_dir = Path(self.entry_prefix) / "per-machine" / machine
        # Check if the directory exists in the password store before trying to delete
        result = self._run_pass(machine, "ls", str(machine_dir), check=False)
        if result.returncode == 0:
            self._run_pass(
                machine, "rm", "--force", "--recursive", str(machine_dir), check=True
            )
        return []

    def generate_hash(self, machine: str) -> bytes:
        result = self._run_pass(
            machine, "git", "log", "-1", "--format=%H", self.entry_prefix, check=False
        )
        git_hash = result.stdout.strip()

        if not git_hash:
            return b""

        from clan_cli.vars.generate import Generator

        manifest = []
        generators = Generator.get_machine_generators(machine, self.flake)
        for generator in generators:
            for file in generator.files:
                manifest.append(f"{generator.name}/{file.name}".encode())

        manifest.append(git_hash)
        return b"\n".join(manifest)

    def needs_upload(self, machine: str, host: Host) -> bool:
        local_hash = self.generate_hash(machine)
        if not local_hash:
            return True

        from clan_lib.cmd import Log, RunOpts

        remote_hash = host.run(
            [
                "cat",
                f"{self.flake.select_machine(machine, 'config.clan.core.vars.password-store.secretLocation')}/.pass_info",
            ],
            RunOpts(log=Log.STDERR, check=False),
        ).stdout.strip()

        if not remote_hash:
            return True

        return local_hash != remote_hash.encode()

    def populate_dir(self, machine: str, output_dir: Path, phases: list[str]) -> None:
        from clan_cli.vars.generate import Generator

        vars_generators = Generator.get_machine_generators(machine, self.flake)
        if "users" in phases:
            with tarfile.open(
                output_dir / "secrets_for_users.tar.gz", "w:gz"
            ) as user_tar:
                for generator in vars_generators:
                    dir_exists = False
                    for file in generator.files:
                        if not file.deploy:
                            continue
                        if not file.secret:
                            continue
                        tar_file = tarfile.TarInfo(name=f"{generator.name}/{file.name}")
                        content = self.get(generator, file.name)
                        tar_file.size = len(content)
                        tar_file.mode = file.mode
                        user_tar.addfile(tarinfo=tar_file, fileobj=io.BytesIO(content))

        if "services" in phases:
            with tarfile.open(output_dir / "secrets.tar.gz", "w:gz") as tar:
                for generator in vars_generators:
                    dir_exists = False
                    for file in generator.files:
                        if not file.deploy:
                            continue
                        if not file.secret:
                            continue
                        if not dir_exists:
                            tar_dir = tarfile.TarInfo(name=generator.name)
                            tar_dir.type = tarfile.DIRTYPE
                            tar_dir.mode = 0o511
                            tar.addfile(tarinfo=tar_dir)
                            dir_exists = True
                        tar_file = tarfile.TarInfo(name=f"{generator.name}/{file.name}")
                        content = self.get(generator, file.name)
                        tar_file.size = len(content)
                        tar_file.mode = file.mode
                        tar_file.uname = file.owner
                        tar_file.gname = file.group
                        tar.addfile(tarinfo=tar_file, fileobj=io.BytesIO(content))
        if "activation" in phases:
            for generator in vars_generators:
                for file in generator.files:
                    if file.needed_for == "activation":
                        out_file = (
                            output_dir / "activation" / generator.name / file.name
                        )
                        out_file.parent.mkdir(parents=True, exist_ok=True)
                        out_file.write_bytes(self.get(generator, file.name))
        if "partitioning" in phases:
            for generator in vars_generators:
                for file in generator.files:
                    if file.needed_for == "partitioning":
                        out_file = (
                            output_dir / "partitioning" / generator.name / file.name
                        )
                        out_file.parent.mkdir(parents=True, exist_ok=True)
                        out_file.write_bytes(self.get(generator, file.name))

        hash_data = self.generate_hash(machine)
        if hash_data:
            (output_dir / ".pass_info").write_bytes(hash_data)

    def upload(self, machine: str, host: Host, phases: list[str]) -> None:
        if "partitioning" in phases:
            msg = "Cannot upload partitioning secrets"
            raise NotImplementedError(msg)
        if not self.needs_upload(machine, host):
            log.info("Secrets already uploaded")
            return
        with TemporaryDirectory(prefix="vars-upload-") as _tempdir:
            pass_dir = Path(_tempdir).resolve()
            self.populate_dir(machine, pass_dir, phases)
            upload_dir = Path(
                self.flake.select_machine(
                    machine, "config.clan.core.vars.password-store.secretLocation"
                )
            )
            upload(host, pass_dir, upload_dir)
