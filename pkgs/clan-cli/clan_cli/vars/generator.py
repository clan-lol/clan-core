import logging
import os
import shutil
import sys
from collections.abc import Iterable
from contextlib import ExitStack
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from clan_lib import bwrap
from clan_lib.cmd import RunOpts, run
from clan_lib.errors import ClanError
from clan_lib.git import commit_files
from clan_lib.nix import nix_config, nix_shell, nix_test_store

from .prompt import Prompt, ask
from .var import Var

if TYPE_CHECKING:
    from clan_lib.flake import Flake

    from ._types import StoreBase

from clan_lib.machines.machines import Machine

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
    validation_hash: str | None = None

    machine: str | None = None
    _flake: "Flake | None" = None
    _public_store: "StoreBase | None" = None
    _secret_store: "StoreBase | None" = None

    @property
    def key(self) -> GeneratorKey:
        return GeneratorKey(machine=self.machine, name=self.name)

    def __hash__(self) -> int:
        return hash(self.key)

    @property
    def exists(self) -> bool:
        """Check if all files for this generator exist in their respective stores."""
        if self._public_store is None or self._secret_store is None:
            msg = "Stores must be set to check existence"
            raise ClanError(msg)

        # Check if all files exist
        for file in self.files:
            store = self._secret_store if file.secret else self._public_store
            if not store.exists(self, file.name):
                return False

        # Also check if validation hashes are up to date
        return self._secret_store.hash_is_valid(
            self
        ) and self._public_store.hash_is_valid(self)

    @classmethod
    def get_machine_selectors(
        cls: type["Generator"],
        machine_names: Iterable[str],
    ) -> list[str]:
        """Get all selectors needed to fetch generators and files for the given machines.

        Args:
            machine_names: The names of the machines.

        Returns:
            list[str]: A list of selectors to fetch all generators and files for the machines.

        """
        config = nix_config()
        system = config["system"]

        generators_selector = "config.clan.core.vars.generators.*.{share,dependencies,migrateFact,prompts,validationHash}"
        files_selector = "config.clan.core.vars.generators.*.files.*.{secret,deploy,owner,group,mode,neededFor}"

        all_selectors = []
        for machine_name in machine_names:
            all_selectors += [
                f'clanInternals.machines."{system}"."{machine_name}".{generators_selector}',
                f'clanInternals.machines."{system}"."{machine_name}".{files_selector}',
                f'clanInternals.machines."{system}"."{machine_name}".config.clan.core.vars.settings.publicModule',
                f'clanInternals.machines."{system}"."{machine_name}".config.clan.core.vars.settings.secretModule',
            ]
        return all_selectors

    @classmethod
    def get_machine_generators(
        cls: type["Generator"],
        machine_names: Iterable[str],
        flake: "Flake",
        include_previous_values: bool = False,
    ) -> list["Generator"]:
        """Get all generators for a machine from the flake.

        Args:
            machine_names: The names of the machines.
            flake: The flake to get the generators from.
            include_previous_values: Whether to include previous values in the generators.

        Returns:
            list[Generator]: A list of (unsorted) generators for the machine.

        """
        generators_selector = "config.clan.core.vars.generators.*.{share,dependencies,migrateFact,prompts,validationHash}"
        files_selector = "config.clan.core.vars.generators.*.files.*.{secret,deploy,owner,group,mode,neededFor}"
        flake.precache(cls.get_machine_selectors(machine_names))

        generators = []
        shared_generators_raw: dict[
            str, tuple[str, dict, dict]
        ] = {}  # name -> (machine_name, gen_data, files_data)

        for machine_name in machine_names:
            # Get all generator metadata in one select (safe fields only)
            generators_data = flake.select_machine(
                machine_name,
                generators_selector,
            )
            if not generators_data:
                continue

            # Get all file metadata in one select
            files_data = flake.select_machine(
                machine_name,
                files_selector,
            )

            machine = Machine(name=machine_name, flake=flake)
            pub_store = machine.public_vars_store
            sec_store = machine.secret_vars_store

            for gen_name, gen_data in generators_data.items():
                # Check for conflicts in shared generator definitions using raw data
                if gen_data["share"]:
                    if gen_name in shared_generators_raw:
                        prev_machine, prev_gen_data, prev_files_data = (
                            shared_generators_raw[gen_name]
                        )
                        # Compare raw data
                        prev_gen_files = prev_files_data.get(gen_name, {})
                        curr_gen_files = files_data.get(gen_name, {})
                        # Build list of differences with details
                        differences = []
                        if prev_gen_files != curr_gen_files:
                            differences.append("files")
                        if prev_gen_data.get("prompts") != gen_data.get("prompts"):
                            differences.append("prompts")
                        if prev_gen_data.get("dependencies") != gen_data.get(
                            "dependencies"
                        ):
                            differences.append("dependencies")
                        if prev_gen_data.get("validationHash") != gen_data.get(
                            "validationHash"
                        ):
                            differences.append("validation_hash")
                        if differences:
                            msg = f"Machines {prev_machine} and {machine_name} have different definitions for shared generator '{gen_name}' (differ in: {', '.join(differences)})"
                            raise ClanError(msg)
                    else:
                        shared_generators_raw[gen_name] = (
                            machine_name,
                            gen_data,
                            files_data,
                        )
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
                prompts = [
                    Prompt.from_nix(p) for p in gen_data.get("prompts", {}).values()
                ]

                share = gen_data["share"]

                generator = cls(
                    name=gen_name,
                    share=share,
                    files=files,
                    dependencies=[
                        GeneratorKey(
                            machine=None
                            if generators_data[dep]["share"]
                            else machine_name,
                            name=dep,
                        )
                        for dep in gen_data["dependencies"]
                    ],
                    migrate_fact=gen_data.get("migrateFact"),
                    validation_hash=gen_data.get("validationHash"),
                    prompts=prompts,
                    # only set machine for machine-specific generators
                    # this is essential for the graph algorithms to work correctly
                    machine=None if share else machine_name,
                    _flake=flake,
                    _public_store=pub_store,
                    _secret_store=sec_store,
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

    def final_script_selector(self, machine_name: str) -> str:
        if self._flake is None:
            msg = "Flake cannot be None"
            raise ClanError(msg)
        return self._flake.machine_selector(
            machine_name, f'config.clan.core.vars.generators."{self.name}".finalScript'
        )

    def final_script(self, machine: "Machine") -> Path:
        if self._flake is None:
            msg = "Flake cannot be None"
            raise ClanError(msg)
        output = Path(self._flake.select(self.final_script_selector(machine.name)))
        if tmp_store := nix_test_store():
            output = tmp_store.joinpath(*output.parts[1:])
        return output

    def validation(self) -> str | None:
        return self.validation_hash

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
        generators = self.get_machine_generators([machine.name], machine.flake)
        result: dict[str, dict[str, bytes]] = {}

        for dep_key in set(self.dependencies):
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

            final_script = self.final_script(machine)

            if sys.platform == "linux" and bwrap.bubblewrap_works():
                cmd = bubblewrap_cmd(str(final_script), tmpdir)
            elif sys.platform == "darwin":
                from clan_lib.sandbox_exec import sandbox_exec_cmd  # noqa: PLC0415

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
                    file_paths = machine.secret_vars_store.set(
                        self,
                        file,
                        secret_file.read_bytes(),
                        machine.name,
                    )
                    secret_changed = True
                else:
                    file_paths = machine.public_vars_store.set(
                        self,
                        file,
                        secret_file.read_bytes(),
                        machine.name,
                    )
                    public_changed = True
                files_to_commit.extend(file_paths)

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
