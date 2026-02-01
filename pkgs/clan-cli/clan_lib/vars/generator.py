import dataclasses
import difflib
import logging
import os
import pprint
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
from clan_lib.nix import nix_config, nix_test_store
from clan_lib.nix_selectors import (
    inventory_relative_directory,
    secrets_age_plugins,
    vars_generators_files,
    vars_generators_metadata,
    vars_password_store_pass_command,
    vars_password_store_secret_location,
    vars_settings_public_module,
    vars_settings_secret_module,
    vars_sops_default_groups,
    vars_sops_secret_upload_dir,
)

from .prompt import Prompt, ask
from .var import Var

if TYPE_CHECKING:
    from clan_lib.flake import Flake

    from ._types import StoreBase

from clan_lib.machines.machines import Machine

from ._types import GeneratorId, PerMachine, Placement, Shared

log = logging.getLogger(__name__)


def pretty_diff_objects(
    prev_value: object,
    curr_value: object,
    prev_label: str,
    curr_label: str,
) -> str:
    """Return a unified diff string between two values."""
    prev_lines = pprint.pformat(prev_value).splitlines()
    curr_lines = pprint.pformat(curr_value).splitlines()
    diff = difflib.unified_diff(
        prev_lines,
        curr_lines,
        fromfile=prev_label,
        tofile=curr_label,
        lineterm="",
    )
    return "\n".join(diff)


def filter_machine_specific_attrs(files: dict[str, dict]) -> dict[str, dict]:
    """Filter out machine-specific attributes that can differ per machine.

    Removes attributes like owner, group, and mode that don't affect
    the equivalency of shared vars across different platforms.
    """
    machine_specific_attrs = {"owner", "group", "mode"}
    return {
        name: {k: v for k, v in attrs.items() if k not in machine_specific_attrs}
        for name, attrs in files.items()
    }


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


def get_machine_selectors(machine_names: Iterable[str]) -> list[str]:
    """Get all selectors needed to fetch generators and files for the given machines.

    Args:
        machine_names: The names of the machines.

    Returns:
        list[str]: A list of selectors to fetch all generators and files for the machines.

    """
    config = nix_config()
    system = config["system"]

    return [
        secrets_age_plugins(),
        inventory_relative_directory(),
        vars_generators_metadata(system, machine_names),
        vars_generators_files(system, machine_names),
        vars_sops_default_groups(system, machine_names),
        vars_settings_public_module(system, machine_names),
        vars_settings_secret_module(system, machine_names),
        vars_sops_secret_upload_dir(system, machine_names),
        vars_password_store_pass_command(system, machine_names),
        vars_password_store_secret_location(system, machine_names),
    ]


def validate_dependencies(
    generator_name: str,
    machine_name: str,
    dependencies: list[str],
    generators_data: dict[str, dict],
) -> list[GeneratorId]:
    """Validate and build dependency keys for a generator.

    Args:
        generator_name: Name of the generator that has dependencies
        machine_name: Name of the machine the generator belongs to
        dependencies: List of dependency generator names
        generators_data: Dictionary of all available generators for this machine

    Returns:
        List of GeneratorId objects

    Raises:
        ClanError: If a dependency does not exist

    """
    deps_list = []
    for dep in dependencies:
        if dep not in generators_data:
            msg = f"Generator '{generator_name}' on machine '{machine_name}' depends on generator '{dep}', but '{dep}' does not exist. Please check your configuration."
            raise ClanError(msg)
        placement: Placement = (
            Shared()
            if generators_data[dep]["share"]
            else PerMachine(machine=machine_name)
        )
        deps_list.append(GeneratorId(name=dep, placement=placement))
    return deps_list


def find_generator_differences(
    gen_name: str,
    ref_machine: str,
    ref_data: dict,
    ref_files: dict,
    curr_machine: str,
    curr_data: dict,
    curr_files: dict,
) -> list[str]:
    """Find differences between two generator definitions.

    Compares the following fields:

    files, prompts, dependencies, validationHash

    Returns:
        List of field names that differ.

    """
    differences = []

    if ref_files != curr_files:
        log.debug(
            f"Files differ for generator '{gen_name}':\n{pretty_diff_objects(ref_files, curr_files, ref_machine, curr_machine)}"
        )
        differences.append("files")
    if ref_data.get("prompts") != curr_data.get("prompts"):
        log.debug(
            f"Prompts differ for generator '{gen_name}':\n{pretty_diff_objects(ref_data.get('prompts'), curr_data.get('prompts'), ref_machine, curr_machine)}"
        )
        differences.append("prompts")
    if ref_data.get("dependencies") != curr_data.get("dependencies"):
        log.debug(
            f"Dependencies differ for generator '{gen_name}':\n{pretty_diff_objects(ref_data.get('dependencies'), curr_data.get('dependencies'), ref_machine, curr_machine)}"
        )
        differences.append("dependencies")
    if ref_data.get("validationHash") != curr_data.get("validationHash"):
        log.debug(
            f"Validation hash differs for generator '{gen_name}':\n"
            f"  {ref_machine}={ref_data.get('validationHash')}\n"
            f"  {curr_machine}={curr_data.get('validationHash')}"
        )
        differences.append("validation_hash")

    return differences


def get_machine_generators(
    machine_names: Iterable[str],
    flake: "Flake",
    secret_cache: dict[Path, bytes] | None = None,
) -> list["Generator"]:
    """Get all generators for a machine from the flake.

    Args:
        machine_names: The names of the machines.
        flake: The flake to get the generators from.
        secret_cache: Optional cache for decrypted secrets to avoid repeated decryption.

    Returns:
        list[Generator]: A list of (unsorted) generators for the machine.

    """
    generators_selector = (
        "config.clan.core.vars.generators.*.{share,dependencies,prompts,validationHash}"
    )
    files_selector = "config.clan.core.vars.generators.*.files.*.{secret,deploy,owner,group,mode,neededFor}"
    flake.precache(get_machine_selectors(machine_names))

    generators: list[Generator] = []
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
                    prev_gen_files = filter_machine_specific_attrs(
                        prev_files_data.get(gen_name, {})
                    )
                    curr_gen_files = filter_machine_specific_attrs(
                        files_data.get(gen_name, {})
                    )

                    # Build list of differences with details
                    differences = find_generator_differences(
                        gen_name=gen_name,
                        ref_machine=prev_machine,
                        ref_data=prev_gen_data,
                        ref_files=prev_gen_files,
                        curr_machine=machine_name,
                        curr_data=gen_data,
                        curr_files=curr_gen_files,
                    )
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
            files: list[Var] = []
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

            share = gen_data["share"]
            placement: Placement = (
                Shared() if share else PerMachine(machine=machine_name)
            )

            generator = Generator(
                key=GeneratorId(name=gen_name, placement=placement),
                files=files,
                dependencies=validate_dependencies(
                    gen_name,
                    machine_name,
                    gen_data["dependencies"],
                    generators_data,
                ),
                validation_hash=gen_data.get("validationHash"),
                prompts=prompts,
                # shared generators can have multiple machines, machine-specific have one
                machines=[machine_name],
                _flake=flake,
                _public_store=pub_store,
                _secret_store=sec_store,
                _secret_cache=secret_cache if secret_cache is not None else {},
            )

            # link generator to its files
            for file in files:
                file.generator(generator)

            if share:
                # For shared generators, check if we already created it
                existing = next(
                    (g for g in generators if g.name == gen_name and g.share), None
                )
                if existing:
                    # Just append the machine to the existing generator
                    existing.machines.append(machine_name)
                else:
                    # Add the new shared generator
                    generators.append(generator)
            else:
                # Always add per-machine generators
                generators.append(generator)

    return generators


@dataclass
class Generator:
    key: GeneratorId
    files: list[Var] = field(default_factory=list)
    prompts: list[Prompt] = field(default_factory=list)
    dependencies: list[GeneratorId] = field(default_factory=list)

    validation_hash: str | None = None

    machines: list[str] = field(default_factory=list)
    """
    List of fixed length 1 for machine-specific generators, or
    multiple machines for shared generators.
    """
    _flake: "Flake | None" = None
    _public_store: "StoreBase | None" = None
    _secret_store: "StoreBase | None" = None

    _secret_cache: dict[Path, bytes] = field(default_factory=dict, repr=False)
    _previous_values: dict[str, str | None] = field(
        default_factory=dict, repr=False, compare=False
    )

    @property
    def share(self) -> bool:
        return isinstance(self.key.placement, Shared)

    @property
    def name(self) -> str:
        return self.key.name

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
            if not store.exists(self.key, file.name):
                return False

        # Also check if validation hashes are up to date
        return self._secret_store.hash_is_valid(
            self.key, self.validation()
        ) and self._public_store.hash_is_valid(self.key, self.validation())

    def get_previous_value(
        self,
        prompt: Prompt,
    ) -> str | None:
        """Lazily compute and cache the previous value for a prompt.

        Uses self._secret_cache for decryption caching across prompts,
        and self._previous_values for result-level caching.
        """
        if not prompt.persist:
            return None

        if prompt.name in self._previous_values:
            return self._previous_values[prompt.name]

        if self._public_store is None or self._secret_store is None:
            msg = "Stores must be set to get previous values"
            raise ClanError(msg)

        result: str | None = None
        if self._public_store.exists(self.key, prompt.name):
            result = self._public_store.get(self.key, prompt.name).decode()
        elif self._secret_store.exists(self.key, prompt.name):
            result = self._secret_store.get(
                self.key, prompt.name, cache=self._secret_cache
            ).decode()

        if result is not None:
            # Cache the result. Don't cache "None"
            self._previous_values[prompt.name] = result

        return result

    def final_script_selector(self, machine_name: str) -> str:
        if self._flake is None:
            msg = "Flake cannot be None"
            raise ClanError(msg)
        return self._flake.machine_selector(
            machine_name, f'config.clan.core.vars.generators."{self.name}".finalScript'
        )

    def final_script(self, machine_name: str) -> Path:
        if self._flake is None:
            msg = "Flake cannot be None"
            raise ClanError(msg)
        output = Path(self._flake.select(self.final_script_selector(machine_name)))
        if tmp_store := nix_test_store():
            output = tmp_store.joinpath(*output.parts[1:])
        return output

    def validation(self) -> str | None:
        return self.validation_hash

    def with_toggled_share(self, machine: str) -> "Generator":
        new_machines: list[str]
        if self.share:
            new_key = GeneratorId(name=self.name, placement=PerMachine(machine=machine))
            new_machines = [machine]
        else:
            new_key = GeneratorId(name=self.name, placement=Shared())
            new_machines = []
        return dataclasses.replace(self, key=new_key, machines=new_machines)

    def decrypt_dependencies(
        self,
        machine_name: str,
    ) -> dict[str, dict[str, bytes]]:
        """Decrypt and retrieve all dependency values for this generator.

        Args:
            machine_name: The machine name used to look up generators.

        Returns:
            Dictionary mapping generator names to their variable values

        """
        if (
            self._flake is None
            or self._public_store is None
            or self._secret_store is None
        ):
            msg = "Flake and stores must be set to decrypt dependencies"
            raise ClanError(msg)

        generators = get_machine_generators([machine_name], self._flake)
        result: dict[str, dict[str, bytes]] = {}

        for dep_key in set(self.dependencies):
            result[dep_key.name] = {}

            dep_generator = next(
                (g for g in generators if g.name == dep_key.name),
                None,
            )
            if dep_generator is None:
                msg = f"Generator {dep_key.name} not found in machine {machine_name}"
                raise ClanError(msg)

            # Check that shared generators don't depend on machine-specific generators
            if self.share and not dep_generator.share:
                msg = f"Shared generators must not depend on machine specific generators. Generator '{self.name}' (shared) depends on '{dep_generator.name}' (machine-specific)"
                raise ClanError(msg)

            dep_files = dep_generator.files
            for file in dep_files:
                if file.secret:
                    result[dep_key.name][file.name] = self._secret_store.get(
                        dep_generator.key,
                        file.name,
                    )
                else:
                    result[dep_key.name][file.name] = self._public_store.get(
                        dep_generator.key,
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
                self.machines,  # For pretty printing of "ask" context
                previous_value=self.get_previous_value(prompt),
            )
        return prompt_values

    def execute(
        self,
        machine_name: str,
        prompt_values: dict[str, str] | None = None,
        no_sandbox: bool = False,
    ) -> None:
        """Execute this generator to produce its output files.

        Args:
            machine_name: The machine name for nix evaluation and store operations.
            prompt_values: Optional dictionary of prompt values. If not provided, prompts will be asked interactively.
            no_sandbox: Whether to disable sandboxing when executing the generator

        """
        if (
            self._flake is None
            or self._public_store is None
            or self._secret_store is None
        ):
            msg = "Flake and stores must be set to execute generator"
            raise ClanError(msg)

        if prompt_values is None:
            prompt_values = self.ask_prompts()

        # build temporary file tree of dependencies
        decrypted_dependencies = self.decrypt_dependencies(machine_name)

        def get_prompt_value(prompt_name: str) -> str:
            try:
                return prompt_values[prompt_name]
            except KeyError as e:
                msg = f"prompt value for '{prompt_name}' in generator {self.name} not provided"
                raise ClanError(msg) from e

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

            final_script = self.final_script(machine_name)

            if sys.platform == "linux" and bwrap.bubblewrap_works() and not no_sandbox:
                from clan_lib.sandbox_exec import bubblewrap_cmd  # noqa: PLC0415

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
                    file_paths = self._secret_store.set(
                        self,
                        file,
                        secret_file.read_bytes(),
                        machine_name,
                    )
                    secret_changed = True
                else:
                    file_paths = self._public_store.set(
                        self,
                        file,
                        secret_file.read_bytes(),
                        machine_name,
                    )
                    public_changed = True
                files_to_commit.extend(file_paths)

            validation = self.validation()
            if public_changed:
                files_to_commit += self._public_store.set_validation(
                    self.key, validation
                )
            if secret_changed:
                files_to_commit += self._secret_store.set_validation(
                    self.key, validation
                )

        commit_files(
            files_to_commit,
            self._flake.path,
            f"Update vars via generator {self.name} for machine {machine_name}",
        )
