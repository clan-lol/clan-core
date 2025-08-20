import logging
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import TYPE_CHECKING

from clan_lib.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_test_store

from .check import check_vars
from .prompt import Prompt
from .var import Var

if TYPE_CHECKING:
    from ._types import StoreBase

log = logging.getLogger(__name__)


def dependencies_as_dir(
    decrypted_dependencies: dict[str, dict[str, bytes]],
    tmpdir: Path,
) -> None:
    """Helper function to create directory structure from decrypted dependencies."""
    for dep_generator, files in decrypted_dependencies.items():
        dep_generator_dir = tmpdir / dep_generator
        dep_generator_dir.mkdir(mode=0o700, parents=False, exist_ok=False)
        for file_name, file in files.items():
            file_path = dep_generator_dir / file_name
            file_path.touch(mode=0o600, exist_ok=False)
            file_path.write_bytes(file)


@dataclass(frozen=True)
class GeneratorKey:
    """A key uniquely identifying a generator within a clan."""

    machine: str | None
    name: str


@dataclass
class Generator:
    name: str
    files: list[Var] = field(default_factory=list)
    share: bool = False
    prompts: list[Prompt] = field(default_factory=list)
    dependencies: list[GeneratorKey] = field(default_factory=list)

    migrate_fact: str | None = None

    machine: str | None = None
    _flake: "Flake | None" = None

    @property
    def key(self) -> GeneratorKey:
        return GeneratorKey(machine=self.machine, name=self.name)

    def __hash__(self) -> int:
        return hash(self.key)

    @cached_property
    def exists(self) -> bool:
        assert self.machine is not None
        assert self._flake is not None
        return check_vars(self.machine, self._flake, generator_name=self.name)

    @classmethod
    def get_machine_generators(
        cls: type["Generator"],
        machine_name: str,
        flake: "Flake",
        include_previous_values: bool = False,
    ) -> list["Generator"]:
        """Get all generators for a machine from the flake.

        Args:
            machine_name (str): The name of the machine.
            flake (Flake): The flake to get the generators from.

        Returns:
            list[Generator]: A list of (unsorted) generators for the machine.

        """
        # Get all generator metadata in one select (safe fields only)
        generators_data = flake.select_machine(
            machine_name,
            "config.clan.core.vars.generators.*.{share,dependencies,migrateFact,prompts}",
        )
        if not generators_data:
            return []

        # Get all file metadata in one select
        files_data = flake.select_machine(
            machine_name,
            "config.clan.core.vars.generators.*.files.*.{secret,deploy,owner,group,mode,neededFor}",
        )

        from clan_lib.machines.machines import Machine

        machine = Machine(name=machine_name, flake=flake)
        pub_store = machine.public_vars_store
        sec_store = machine.secret_vars_store

        generators = []
        for gen_name, gen_data in generators_data.items():
            # Build files from the files_data
            files = []
            gen_files = files_data.get(gen_name, {})
            for file_name, file_data in gen_files.items():
                var = Var(
                    id=f"{gen_name}/{file_name}",
                    name=file_name,
                    secret=file_data["secret"],
                    deploy=file_data["deploy"],
                    owner=file_data["owner"],
                    group=file_data["group"],
                    mode=(
                        file_data["mode"]
                        if isinstance(file_data["mode"], int)
                        else int(file_data["mode"], 8)
                    ),
                    needed_for=file_data["neededFor"],
                    _store=pub_store if not file_data["secret"] else sec_store,
                )
                files.append(var)

            # Build prompts
            prompts = [Prompt.from_nix(p) for p in gen_data.get("prompts", {}).values()]

            generator = cls(
                name=gen_name,
                share=gen_data["share"],
                files=files,
                dependencies=[
                    GeneratorKey(machine=machine_name, name=dep)
                    for dep in gen_data["dependencies"]
                ],
                migrate_fact=gen_data.get("migrateFact"),
                prompts=prompts,
                machine=machine_name,
                _flake=flake,
            )
            generators.append(generator)

        # TODO: This should be done in a non-mutable way.
        if include_previous_values:
            for generator in generators:
                for prompt in generator.prompts:
                    prompt.previous_value = generator.get_previous_value(
                        machine,
                        prompt,
                    )

        return generators

    def get_previous_value(
        self,
        machine: "Machine",
        prompt: Prompt,
    ) -> str | None:
        if not prompt.persist:
            return None

        pub_store = machine.public_vars_store
        if pub_store.exists(self, prompt.name):
            return pub_store.get(self, prompt.name).decode()
        sec_store = machine.secret_vars_store
        if sec_store.exists(self, prompt.name):
            return sec_store.get(self, prompt.name).decode()
        return None

    def final_script(self) -> Path:
        assert self.machine is not None
        assert self._flake is not None
        from clan_lib.machines.machines import Machine

        machine = Machine(name=self.machine, flake=self._flake)
        output = Path(
            machine.select(
                f'config.clan.core.vars.generators."{self.name}".finalScript',
            ),
        )
        if tmp_store := nix_test_store():
            output = tmp_store.joinpath(*output.parts[1:])
        return output

    def validation(self) -> str | None:
        assert self.machine is not None
        assert self._flake is not None
        from clan_lib.machines.machines import Machine

        machine = Machine(name=self.machine, flake=self._flake)
        return machine.select(
            f'config.clan.core.vars.generators."{self.name}".validationHash',
        )

    def decrypt_dependencies(
        self,
        machine: "Machine",
        secret_vars_store: "StoreBase",
        public_vars_store: "StoreBase",
    ) -> dict[str, dict[str, bytes]]:
        """Decrypt and retrieve all dependency values for this generator.

        Args:
            machine: The machine context
            secret_vars_store: Store for secret variables
            public_vars_store: Store for public variables

        Returns:
            Dictionary mapping generator names to their variable values

        """
        from clan_lib.errors import ClanError

        generators = self.get_machine_generators(machine.name, machine.flake)
        result: dict[str, dict[str, bytes]] = {}

        for dep_key in set(self.dependencies):
            # For now, we only support dependencies from the same machine
            if dep_key.machine != machine.name:
                msg = f"Cross-machine dependencies are not supported. Generator {self.name} depends on {dep_key.name} from machine {dep_key.machine}"
                raise ClanError(msg)

            result[dep_key.name] = {}

            dep_generator = next(
                (g for g in generators if g.name == dep_key.name),
                None,
            )
            if dep_generator is None:
                msg = f"Generator {dep_key.name} not found in machine {machine.name}"
                raise ClanError(msg)

            # Check that shared generators don't depend on machine-specific generators
            if self.share and not dep_generator.share:
                msg = f"Shared generators must not depend on machine specific generators. Generator '{self.name}' (shared) depends on '{dep_generator.name}' (machine-specific)"
                raise ClanError(msg)

            dep_files = dep_generator.files
            for file in dep_files:
                if file.secret:
                    result[dep_key.name][file.name] = secret_vars_store.get(
                        dep_generator,
                        file.name,
                    )
                else:
                    result[dep_key.name][file.name] = public_vars_store.get(
                        dep_generator,
                        file.name,
                    )
        return result

    def ask_prompts(self) -> dict[str, str]:
        """Interactively ask for all prompt values for this generator.

        Returns:
            Dictionary mapping prompt names to their values

        """
        from .prompt import ask

        prompt_values: dict[str, str] = {}
        for prompt in self.prompts:
            var_id = f"{self.name}/{prompt.name}"
            prompt_values[prompt.name] = ask(
                var_id,
                prompt.prompt_type,
                prompt.description if prompt.description != prompt.name else None,
            )
        return prompt_values

    def execute(
        self,
        machine: "Machine",
        prompt_values: dict[str, str] | None = None,
        no_sandbox: bool = False,
    ) -> None:
        """Execute this generator to produce its output files.

        Args:
            machine: The machine to execute the generator for
            prompt_values: Optional dictionary of prompt values. If not provided, prompts will be asked interactively.
            no_sandbox: Whether to disable sandboxing when executing the generator

        """
        import os
        import sys
        from contextlib import ExitStack
        from pathlib import Path
        from tempfile import TemporaryDirectory

        from clan_lib import bwrap
        from clan_lib.cmd import RunOpts, run
        from clan_lib.errors import ClanError
        from clan_lib.git import commit_files

        if prompt_values is None:
            prompt_values = self.ask_prompts()

        # build temporary file tree of dependencies
        decrypted_dependencies = self.decrypt_dependencies(
            machine,
            machine.secret_vars_store,
            machine.public_vars_store,
        )

        def get_prompt_value(prompt_name: str) -> str:
            try:
                return prompt_values[prompt_name]
            except KeyError as e:
                msg = f"prompt value for '{prompt_name}' in generator {self.name} not provided"
                raise ClanError(msg) from e

        def bubblewrap_cmd(generator: str, tmpdir: Path) -> list[str]:
            """Helper function to create bubblewrap command."""
            import shutil

            from clan_lib.nix import nix_shell, nix_test_store

            test_store = nix_test_store()
            real_bash_path = Path("bash")
            if os.environ.get("IN_NIX_SANDBOX"):
                bash_executable_path = Path(str(shutil.which("bash")))
                real_bash_path = bash_executable_path.resolve()

            # fmt: off
            return nix_shell(
                ["bash", "bubblewrap"],
                [
                    "bwrap",
                    "--unshare-all",
                    "--tmpfs",  "/",
                    "--ro-bind", "/nix/store", "/nix/store",
                    "--ro-bind", "/bin/sh", "/bin/sh",
                    *(["--ro-bind", str(test_store), str(test_store)] if test_store else []),
                    "--dev", "/dev",
                    "--bind", str(tmpdir), str(tmpdir),
                    "--chdir", "/",
                    "--bind", "/proc", "/proc",
                    "--uid", "1000",
                    "--gid", "1000",
                    "--",
                    str(real_bash_path), "-c", generator,
                ],
            )
            # fmt: on

        env = os.environ.copy()
        with ExitStack() as stack:
            _tmpdir = stack.enter_context(TemporaryDirectory(prefix="vars-"))
            tmpdir = Path(_tmpdir).resolve()
            tmpdir_in = tmpdir / "in"
            tmpdir_prompts = tmpdir / "prompts"
            tmpdir_out = tmpdir / "out"
            tmpdir_in.mkdir()
            tmpdir_out.mkdir()
            env["in"] = str(tmpdir_in)
            env["out"] = str(tmpdir_out)

            # populate dependency inputs
            dependencies_as_dir(decrypted_dependencies, tmpdir_in)

            # populate prompted values
            if self.prompts:
                tmpdir_prompts.mkdir()
                env["prompts"] = str(tmpdir_prompts)
                for prompt in self.prompts:
                    prompt_file = tmpdir_prompts / prompt.name
                    value = get_prompt_value(prompt.name)
                    prompt_file.write_text(value)

            final_script = self.final_script()

            if sys.platform == "linux" and bwrap.bubblewrap_works():
                cmd = bubblewrap_cmd(str(final_script), tmpdir)
            elif sys.platform == "darwin":
                from clan_lib.sandbox_exec import sandbox_exec_cmd

                cmd = stack.enter_context(sandbox_exec_cmd(str(final_script), tmpdir))
            else:
                # For non-sandboxed execution
                if not no_sandbox:
                    msg = (
                        f"Cannot safely execute generator {self.name}: Sandboxing is not available on this system\n"
                        f"Re-run 'vars generate' with '--no-sandbox' to disable sandboxing"
                    )
                    raise ClanError(msg)
                cmd = ["bash", "-c", str(final_script)]

            run(cmd, RunOpts(env=env, cwd=tmpdir))
            files_to_commit = []

            # store secrets
            public_changed = False
            secret_changed = False
            for file in self.files:
                secret_file = tmpdir_out / file.name
                if not secret_file.is_file():
                    msg = f"did not generate a file for '{file.name}' when running the following command:\n"
                    msg += str(final_script)
                    # list all files in the output directory
                    if tmpdir_out.is_dir():
                        msg += "\nOutput files:\n"
                        for f in tmpdir_out.iterdir():
                            msg += f"  - {f.name}\n"
                    raise ClanError(msg)
                if file.secret:
                    file_path = machine.secret_vars_store.set(
                        self,
                        file,
                        secret_file.read_bytes(),
                    )
                    secret_changed = True
                else:
                    file_path = machine.public_vars_store.set(
                        self,
                        file,
                        secret_file.read_bytes(),
                    )
                    public_changed = True
                if file_path:
                    files_to_commit.append(file_path)

            validation = self.validation()
            if validation is not None:
                if public_changed:
                    files_to_commit.append(
                        machine.public_vars_store.set_validation(self, validation),
                    )
                if secret_changed:
                    files_to_commit.append(
                        machine.secret_vars_store.set_validation(self, validation),
                    )

        commit_files(
            files_to_commit,
            machine.flake_dir,
            f"Update vars via generator {self.name} for machine {machine.name}",
        )
