import argparse
import logging
import os
import shutil
import sys
from contextlib import ExitStack
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_services_for_machine,
)
from clan_cli.vars._types import StoreBase
from clan_cli.vars.migration import check_can_migrate, migrate_files
from clan_lib.api import API
from clan_lib.cmd import RunOpts, run
from clan_lib.errors import ClanError
from clan_lib.flake import Flake, require_flake
from clan_lib.git import commit_files
from clan_lib.machines.list import list_full_machines
from clan_lib.nix import nix_config, nix_shell, nix_test_store

from .check import check_vars
from .graph import minimal_closure, requested_closure
from .prompt import Prompt, ask
from .var import Var

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from clan_lib.flake import Flake
    from clan_lib.machines.machines import Machine


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
        """
        Get all generators for a machine from the flake.
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
                    prompt.previous_value = _get_previous_value(
                        machine, generator, prompt
                    )

        return generators

    def final_script(self) -> Path:
        assert self.machine is not None
        assert self._flake is not None
        from clan_lib.machines.machines import Machine

        machine = Machine(name=self.machine, flake=self._flake)
        output = Path(
            machine.select(
                f'config.clan.core.vars.generators."{self.name}".finalScript'
            )
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
            f'config.clan.core.vars.generators."{self.name}".validationHash'
        )


def bubblewrap_cmd(generator: str, tmpdir: Path) -> list[str]:
    test_store = nix_test_store()

    real_bash_path = Path("bash")
    if os.environ.get("IN_NIX_SANDBOX"):
        bash_executable_path = Path(str(shutil.which("bash")))
        real_bash_path = bash_executable_path.resolve()

    # fmt: off
    return nix_shell(
        [
            "bash",
            "bubblewrap",
        ],
        [
            "bwrap",
            "--unshare-all",
            "--tmpfs",  "/",
            "--ro-bind", "/nix/store", "/nix/store",
            "--ro-bind", "/bin/sh", "/bin/sh",
            *(["--ro-bind", str(test_store), str(test_store)] if test_store else []),
            "--dev", "/dev",
            # not allowed to bind procfs in some sandboxes
            "--bind", str(tmpdir), str(tmpdir),
            "--chdir", "/",
            # Doesn't work in our CI?
            #"--proc", "/proc",
            #"--hostname", "facts",
            "--bind", "/proc", "/proc",
            "--uid", "1000",
            "--gid", "1000",
            "--",
            str(real_bash_path), "-c", generator
        ]
    )
    # fmt: on


# TODO: implement caching to not decrypt the same secret multiple times
def decrypt_dependencies(
    machine: "Machine",
    generator: Generator,
    secret_vars_store: StoreBase,
    public_vars_store: StoreBase,
) -> dict[str, dict[str, bytes]]:
    generators = Generator.get_machine_generators(machine.name, machine.flake)

    result: dict[str, dict[str, bytes]] = {}

    for dep_key in set(generator.dependencies):
        # For now, we only support dependencies from the same machine
        if dep_key.machine != machine.name:
            msg = f"Cross-machine dependencies are not supported. Generator {generator.name} depends on {dep_key.name} from machine {dep_key.machine}"
            raise ClanError(msg)

        result[dep_key.name] = {}

        dep_generator = next((g for g in generators if g.name == dep_key.name), None)
        if dep_generator is None:
            msg = f"Generator {dep_key.name} not found in machine {machine.name}"
            raise ClanError(msg)

        dep_files = dep_generator.files
        for file in dep_files:
            if file.secret:
                result[dep_key.name][file.name] = secret_vars_store.get(
                    dep_generator, file.name
                )
            else:
                result[dep_key.name][file.name] = public_vars_store.get(
                    dep_generator, file.name
                )
    return result


# decrypt dependencies and return temporary file tree
def dependencies_as_dir(
    decrypted_dependencies: dict[str, dict[str, bytes]],
    tmpdir: Path,
) -> None:
    for dep_generator, files in decrypted_dependencies.items():
        dep_generator_dir = tmpdir / dep_generator
        # Explicitly specify parents and exist_ok default values for clarity
        dep_generator_dir.mkdir(mode=0o700, parents=False, exist_ok=False)
        for file_name, file in files.items():
            file_path = dep_generator_dir / file_name
            # Avoid the file creation and chmod race
            # If the file already existed,
            # we'd have to create a temp one and rename instead;
            # however, this is a clean dir so there shouldn't be any collisions
            file_path.touch(mode=0o600, exist_ok=False)
            file_path.write_bytes(file)


def _execute_generator(
    machine: "Machine",
    generator: Generator,
    secret_vars_store: StoreBase,
    public_vars_store: StoreBase,
    prompt_values: dict[str, str],
    no_sandbox: bool = False,
) -> None:
    if not isinstance(machine.flake, Path):
        msg = f"flake is not a Path: {machine.flake}"
        msg += "fact/secret generation is only supported for local flakes"

    # build temporary file tree of dependencies
    decrypted_dependencies = decrypt_dependencies(
        machine,
        generator,
        secret_vars_store,
        public_vars_store,
    )

    def get_prompt_value(prompt_name: str) -> str:
        try:
            return prompt_values[prompt_name]
        except KeyError as e:
            msg = f"prompt value for '{prompt_name}' in generator {generator.name} not provided"
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
        # TODO: make prompts rest API friendly
        if generator.prompts:
            tmpdir_prompts.mkdir()
            env["prompts"] = str(tmpdir_prompts)
            for prompt in generator.prompts:
                prompt_file = tmpdir_prompts / prompt.name
                value = get_prompt_value(prompt.name)
                prompt_file.write_text(value)
        from clan_lib import bwrap

        final_script = generator.final_script()

        if sys.platform == "linux" and bwrap.bubblewrap_works():
            cmd = bubblewrap_cmd(str(final_script), tmpdir)
        elif sys.platform == "darwin":
            from clan_lib.sandbox_exec import sandbox_exec_cmd

            cmd = stack.enter_context(sandbox_exec_cmd(str(final_script), tmpdir))
        else:
            # For non-sandboxed execution (Linux without bubblewrap or other platforms)
            if not no_sandbox:
                msg = (
                    f"Cannot safely execute generator {generator.name}: Sandboxing is not available on this system\n"
                    f"Re-run 'vars generate' with '--no-sandbox' to disable sandboxing"
                )
                raise ClanError(msg)
            cmd = ["bash", "-c", str(final_script)]

        run(cmd, RunOpts(env=env, cwd=tmpdir))
        files_to_commit = []
        # store secrets
        files = generator.files
        public_changed = False
        secret_changed = False
        for file in files:
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
                file_path = secret_vars_store.set(
                    generator,
                    file,
                    secret_file.read_bytes(),
                )
                secret_changed = True
            else:
                file_path = public_vars_store.set(
                    generator,
                    file,
                    secret_file.read_bytes(),
                )
                public_changed = True
            if file_path:
                files_to_commit.append(file_path)
            validation = generator.validation()
            if validation is not None:
                if public_changed:
                    files_to_commit.append(
                        public_vars_store.set_validation(generator, validation)
                    )
                if secret_changed:
                    files_to_commit.append(
                        secret_vars_store.set_validation(generator, validation)
                    )
    commit_files(
        files_to_commit,
        machine.flake_dir,
        f"Update vars via generator {generator.name} for machine {machine.name}",
    )


def _ask_prompts(
    generator: Generator,
) -> dict[str, str]:
    prompt_values: dict[str, str] = {}
    for prompt in generator.prompts:
        var_id = f"{generator.name}/{prompt.name}"
        prompt_values[prompt.name] = ask(
            var_id,
            prompt.prompt_type,
            prompt.description if prompt.description != prompt.name else None,
        )
    return prompt_values


def _get_previous_value(
    machine: "Machine",
    generator: Generator,
    prompt: Prompt,
) -> str | None:
    if not prompt.persist:
        return None

    pub_store = machine.public_vars_store
    if pub_store.exists(generator, prompt.name):
        return pub_store.get(generator, prompt.name).decode()
    sec_store = machine.secret_vars_store
    if sec_store.exists(generator, prompt.name):
        return sec_store.get(generator, prompt.name).decode()
    return None


@API.register
def get_generators(
    machine: "Machine",
    full_closure: bool,
    generator_name: str | None = None,
    include_previous_values: bool = False,
) -> list[Generator]:
    """
    Get generators for a machine, with optional closure computation.

    Args:
        machine: The machine to get generators for.
        full_closure: If True, include all dependency generators. If False, only include missing ones.
        generator_name: Name of a specific generator to get, or None for all generators.
        include_previous_values: If True, populate prompts with their previous values.

    Returns:
        List of generators based on the specified selection and closure mode.
    """
    from . import graph

    vars_generators = Generator.get_machine_generators(machine.name, machine.flake)
    generators: dict[GeneratorKey, Generator] = {
        generator.key: generator for generator in vars_generators
    }

    result_closure = []
    if generator_name is None:  # all generators selected
        if full_closure:
            result_closure = graph.full_closure(generators)
        else:
            result_closure = graph.all_missing_closure(generators)
    # specific generator selected
    elif full_closure:
        gen_key = GeneratorKey(machine=machine.name, name=generator_name)
        result_closure = requested_closure([gen_key], generators)
    else:
        gen_key = GeneratorKey(machine=machine.name, name=generator_name)
        result_closure = minimal_closure([gen_key], generators)

    if include_previous_values:
        for generator in result_closure:
            for prompt in generator.prompts:
                prompt.previous_value = _get_previous_value(machine, generator, prompt)

    return result_closure


def _ensure_healthy(
    machine: "Machine",
    generators: list[Generator] | None = None,
) -> None:
    """
    Run health checks on the provided generators.
    Fails if any of the generators' health checks fail.
    """
    if generators is None:
        generators = Generator.get_machine_generators(machine.name, machine.flake)

    pub_healtcheck_msg = machine.public_vars_store.health_check(
        machine.name, generators
    )
    sec_healtcheck_msg = machine.secret_vars_store.health_check(
        machine.name, generators
    )

    if pub_healtcheck_msg or sec_healtcheck_msg:
        msg = f"Health check failed for machine {machine.name}:\n"
        if pub_healtcheck_msg:
            msg += f"Public vars store: {pub_healtcheck_msg}\n"
        if sec_healtcheck_msg:
            msg += f"Secret vars store: {sec_healtcheck_msg}"
        raise ClanError(msg)


def _generate_vars_for_machine(
    machine: "Machine",
    generators: list[Generator],
    all_prompt_values: dict[str, dict[str, str]],
    no_sandbox: bool = False,
) -> None:
    _ensure_healthy(machine=machine, generators=generators)
    for generator in generators:
        if check_can_migrate(machine, generator):
            migrate_files(machine, generator)
        else:
            _execute_generator(
                machine=machine,
                generator=generator,
                secret_vars_store=machine.secret_vars_store,
                public_vars_store=machine.public_vars_store,
                prompt_values=all_prompt_values.get(generator.name, {}),
                no_sandbox=no_sandbox,
            )


@API.register
def run_generators(
    machine_name: str,
    all_prompt_values: dict[str, dict[str, str]],
    base_dir: Path,
    generators: list[str] | None = None,
    no_sandbox: bool = False,
) -> None:
    """Run the specified generators for a machine.
    Args:
        machine_name (str): The name of the machine.
        generators (list[str]): The list of generator names to run.
        all_prompt_values (dict[str, dict[str, str]]): A dictionary mapping generator names
            to their prompt values.
        base_dir (Path): The base directory of the flake.
        no_sandbox (bool): Whether to disable sandboxing when executing the generator.
    Returns:
        bool: True if any variables were generated, False otherwise.
    Raises:
        ClanError: If the machine or generator is not found, or if there are issues with
        executing the generator.
    """
    from clan_lib.machines.machines import Machine

    machine = Machine(name=machine_name, flake=Flake(str(base_dir)))
    if not generators:
        generator_objects = Generator.get_machine_generators(
            machine_name, machine.flake
        )
    else:
        generators_set = set(generators)
        generator_objects = [
            g
            for g in Generator.get_machine_generators(machine_name, machine.flake)
            if g.name in generators_set
        ]
    _generate_vars_for_machine(
        machine=machine,
        generators=generator_objects,
        all_prompt_values=all_prompt_values,
        no_sandbox=no_sandbox,
    )


def create_machine_vars_interactive(
    machine: "Machine",
    generator_name: str | None,
    regenerate: bool,
    no_sandbox: bool = False,
) -> None:
    generators = get_generators(machine, regenerate, generator_name)
    if len(generators) == 0:
        return
    all_prompt_values = {}
    for generator in generators:
        all_prompt_values[generator.name] = _ask_prompts(generator)
    _generate_vars_for_machine(
        machine,
        generators,
        all_prompt_values,
        no_sandbox=no_sandbox,
    )


def generate_vars(
    machines: list["Machine"],
    generator_name: str | None = None,
    regenerate: bool = False,
    no_sandbox: bool = False,
) -> None:
    for machine in machines:
        errors = []
        try:
            create_machine_vars_interactive(
                machine,
                generator_name,
                regenerate,
                no_sandbox=no_sandbox,
            )
            machine.info("All vars are up to date")
        except Exception as exc:
            errors += [(machine, exc)]
        if len(errors) == 1:
            raise errors[0][1]
        if len(errors) > 1:
            msg = f"Failed to generate vars for {len(errors)} hosts:"
            for machine, error in errors:
                msg += f"\n{machine}: {error}"
            raise ClanError(msg) from errors[0][1]


def generate_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machines: list[Machine] = list(list_full_machines(flake).values())

    if len(args.machines) > 0:
        machines = list(
            filter(
                lambda m: m.name in args.machines,
                machines,
            )
        )

    # prefetch all vars
    config = nix_config()
    system = config["system"]
    machine_names = [machine.name for machine in machines]
    # test
    flake.precache(
        [
            f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.generators.*.validationHash",
        ]
    )
    generate_vars(
        machines,
        args.generator,
        args.regenerate,
        no_sandbox=args.no_sandbox,
    )


def register_generate_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machines",
        type=str,
        help="machine to generate facts for. if empty, generate facts for all machines",
        nargs="*",
        default=[],
    )
    add_dynamic_completer(machines_parser, complete_machines)

    service_parser = parser.add_argument(
        "--generator",
        "-g",
        type=str,
        help="execute only the specified generator. If unset, execute all generators",
        default=None,
    )
    add_dynamic_completer(service_parser, complete_services_for_machine)

    parser.add_argument(
        "--regenerate",
        "-r",
        action=argparse.BooleanOptionalAction,
        help="whether to regenerate facts for the specified machine",
        default=None,
    )

    parser.add_argument(
        "--no-sandbox",
        action="store_true",
        help="disable sandboxing when executing the generator. WARNING: potentially executing untrusted code from external clan modules",
        default=False,
    )

    parser.add_argument(
        "--fake-prompts",
        action="store_true",
        help="automatically fill prompt responses for testing (unsafe)",
        default=False,
    )

    parser.set_defaults(func=generate_command)
