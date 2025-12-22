import io
import logging
import os
import shutil
import subprocess
import tarfile
from collections.abc import Iterable
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import override

from clan_lib.cmd import Log, RunOpts
from clan_lib.flake import Flake
from clan_lib.ssh.host import Host
from clan_lib.ssh.upload import upload
from clan_lib.vars._types import StoreBase
from clan_lib.vars.generator import Generator, Var

log = logging.getLogger(__name__)


class SecretStore(StoreBase):
    @property
    def is_secret_store(self) -> bool:
        return True

    def __init__(self, flake: Flake, pass_cmd: str | None = None) -> None:
        super().__init__(flake)
        self.entry_prefix = "clan-vars"
        self._store_dir: Path | None = None
        self._pass_cmd = pass_cmd

    @property
    def store_name(self) -> str:
        return "password_store"

    def store_dir(self) -> Path:
        """Get the password store directory, cached per machine."""
        if self._pass_command() == "passage":
            if "PASSAGE_DIR" in os.environ:
                self._store_dir = Path(os.environ["PASSAGE_DIR"])
            else:
                self._store_dir = Path(os.environ["HOME"] + "/.passage/store")
        elif self._pass_command() == "pass":
            if "PASSWORD_STORE_DIR" in os.environ:
                self._store_dir = Path(os.environ["PASSWORD_STORE_DIR"])
            else:
                self._store_dir = Path(os.environ["HOME"] + "/.password-store")
        else:
            msg = f"Unknown pass command {self._pass_cmd}"
            raise ValueError(msg)
        return self._store_dir

    def cmd_exists(self, cmd: str) -> bool:
        return shutil.which(cmd) is not None

    def init_pass_command(self, machine: str) -> None:
        """Initialize the password store command based on the machine's configuration."""
        pass_cmd = self.flake.select_machine(
            machine,
            "config.clan.core.vars.password-store.passCommand",
        )

        if not self.cmd_exists(pass_cmd):
            msg = f"Could not find {pass_cmd} in PATH. Make sure it is installed"
            raise ValueError(msg)

        self._pass_cmd = str(pass_cmd)

    def _pass_command(self) -> str:
        if not self._pass_cmd:
            msg = "Password store command not initialized. This should be set during SecretStore initialization."
            raise ValueError(msg)
        return self._pass_cmd

    def entry_dir(self, generator: Generator, name: str) -> Path:
        return Path(self.entry_prefix) / self.rel_dir(generator, name)

    def _run_pass(
        self,
        *args: str,
        input: bytes | None = None,  # noqa: A002
        check: bool = True,
    ) -> subprocess.CompletedProcess[bytes]:
        cmd = [self._pass_command(), *args]
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
        machine: str,  # noqa: ARG002
    ) -> Path | None:
        pass_call = ["insert", "-m", str(self.entry_dir(generator, var.name))]
        self._run_pass(*pass_call, input=value, check=True)
        return None  # we manage the files outside of the git repo

    def get(self, generator: Generator, name: str) -> bytes:
        pass_name = str(self.entry_dir(generator, name))
        return self._run_pass("show", pass_name).stdout

    def exists(self, generator: Generator, name: str) -> bool:
        pass_name = str(self.entry_dir(generator, name))
        # Check if the file exists with either .age or .gpg extension
        store_dir = self.store_dir()
        age_file = store_dir / f"{pass_name}.age"
        gpg_file = store_dir / f"{pass_name}.gpg"
        return age_file.exists() or gpg_file.exists()

    def delete(self, generator: Generator, name: str) -> Iterable[Path]:
        pass_name = str(self.entry_dir(generator, name))
        self._run_pass("rm", "--force", pass_name, check=True)
        return []

    def delete_store(self, machine: str) -> Iterable[Path]:
        machine_dir = Path(self.entry_prefix) / "per-machine" / machine
        # Check if the directory exists in the password store before trying to delete
        result = self._run_pass("ls", str(machine_dir), check=False)
        if result.returncode == 0:
            self._run_pass(
                "rm",
                "--force",
                "--recursive",
                str(machine_dir),
                check=True,
            )
        return []

    def generate_hash(self, machine: str) -> bytes:
        result = self._run_pass(
            "git",
            "log",
            "-1",
            "--format=%H",
            self.entry_prefix,
            check=False,
        )
        git_hash = result.stdout.strip()

        if not git_hash:
            return b""

        generators = Generator.get_machine_generators([machine], self.flake)
        manifest = [
            f"{generator.name}/{file.name}".encode()
            for generator in generators
            for file in generator.files
        ]

        manifest.append(git_hash)
        return b"\n".join(manifest)

    def needs_upload(self, machine: str, host: Host) -> bool:
        local_hash = self.generate_hash(machine)
        if not local_hash:
            return True

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
        vars_generators = Generator.get_machine_generators([machine], self.flake)
        if "users" in phases:
            with tarfile.open(
                output_dir / "secrets_for_users.tar.gz",
                "w:gz",
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
                        out_file.write_bytes(file.value)
        if "partitioning" in phases:
            for generator in vars_generators:
                for file in generator.files:
                    if file.needed_for == "partitioning":
                        out_file = (
                            output_dir / "partitioning" / generator.name / file.name
                        )
                        out_file.parent.mkdir(parents=True, exist_ok=True)
                        out_file.write_bytes(file.value)

        hash_data = self.generate_hash(machine)
        if hash_data:
            (output_dir / ".pass_info").write_bytes(hash_data)

    @override
    def get_upload_directory(self, machine: str) -> str:
        return self.flake.select_machine(
            machine,
            "config.clan.core.vars.password-store.secretLocation",
        )

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
            upload(host, pass_dir, Path(self.get_upload_directory(machine)))
