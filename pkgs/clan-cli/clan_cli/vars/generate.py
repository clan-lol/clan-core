import argparse
import logging
import os
import shutil
import sys
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING, Any

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_services_for_machine,
)
from clan_cli.git import commit_files
from clan_cli.machines.list import list_machines
from clan_cli.vars._types import StoreBase
from clan_cli.vars.migration import check_can_migrate, migrate_files
from clan_lib.api import API
from clan_lib.cmd import RunOpts, run
from clan_lib.errors import ClanError
from clan_lib.flake import Flake
from clan_lib.nix import nix_config, nix_shell, nix_test_store

from .check import check_vars
from .graph import (
    minimal_closure,
    requested_closure,
)
from .prompt import Prompt, ask
from .var import Var

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from clan_cli.machines.machines import Machine


@dataclass
class Generator:
    name: str
    files: list[Var] = field(default_factory=list)
    share: bool = False
    prompts: list[Prompt] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    migrate_fact: str | None = None

    # TODO: remove this
    _machine: "Machine | None" = None

    def machine(self, machine: "Machine") -> None:
        self._machine = machine

    @cached_property
    def exists(self) -> bool:
        assert self._machine is not None
        return check_vars(self._machine, generator_name=self.name)

    @classmethod
    def from_json(cls: type["Generator"], data: dict[str, Any]) -> "Generator":
        return cls(
            name=data["name"],
            share=data["share"],
            files=[Var.from_json(data["name"], f) for f in data["files"].values()],
            dependencies=data["dependencies"],
            migrate_fact=data["migrateFact"],
            prompts=[Prompt.from_json(p) for p in data["prompts"].values()],
        )

    def final_script(self) -> Path:
        assert self._machine is not None
        final_script = self._machine.build_nix(
            f'config.clan.core.vars.generators."{self.name}".finalScript'
        )
        return final_script

    def validation(self) -> str | None:
        assert self._machine is not None
        return self._machine.eval_nix(
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
    decrypted_dependencies: dict[str, Any] = {}
    for generator_name in set(generator.dependencies):
        decrypted_dependencies[generator_name] = {}
        for dep_generator in machine.vars_generators():
            if generator_name == dep_generator.name:
                break
        else:
            msg = f"Could not find dependent generator {generator_name} in machine {machine.name}"
            raise ClanError(msg)
        dep_files = dep_generator.files
        for file in dep_files:
            if file.secret:
                decrypted_dependencies[generator_name][file.name] = (
                    secret_vars_store.get(dep_generator, file.name)
                )
            else:
                decrypted_dependencies[generator_name][file.name] = (
                    public_vars_store.get(dep_generator, file.name)
                )
    return decrypted_dependencies


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


def execute_generator(
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
    with TemporaryDirectory(prefix="vars-") as _tmpdir:
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
        from clan_cli import bwrap

        final_script = generator.final_script()

        if sys.platform == "linux":
            if bwrap.bubblewrap_works():
                cmd = bubblewrap_cmd(str(final_script), tmpdir)
            else:
                if not no_sandbox:
                    msg = (
                        f"Cannot safely execute generator {generator.name}: Sandboxing is not available on this system\n"
                        f"Re-run 'vars generate' with '--no-sandbox' to disable sandboxing"
                    )
                    raise ClanError(msg)
                cmd = ["bash", "-c", str(final_script)]
        else:
            # TODO: implement sandboxing for macOS using sandbox-exec
            cmd = ["bash", "-c", str(final_script)]
        run(cmd, RunOpts(env=env))
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


def get_closure(
    machine: "Machine",
    generator_name: str | None,
    regenerate: bool,
    include_previous_values: bool = False,
) -> list[Generator]:
    from .graph import all_missing_closure, full_closure

    vars_generators = machine.vars_generators()
    generators: dict[str, Generator] = {
        generator.name: generator for generator in vars_generators
    }

    # TODO: we should remove this
    for generator in vars_generators:
        generator.machine(machine)

    result_closure = []
    if generator_name is None:  # all generators selected
        if regenerate:
            result_closure = full_closure(generators)
        else:
            result_closure = all_missing_closure(generators)
    # specific generator selected
    elif regenerate:
        result_closure = requested_closure([generator_name], generators)
    else:
        result_closure = minimal_closure([generator_name], generators)

    if include_previous_values:
        for generator in result_closure:
            for prompt in generator.prompts:
                prompt.previous_value = _get_previous_value(machine, generator, prompt)

    return result_closure


@API.register
def get_generators_closure(
    machine_name: str,
    base_dir: Path,
    regenerate: bool = False,
    include_previous_values: bool = False,
) -> list[Generator]:
    from clan_cli.machines.machines import Machine

    return get_closure(
        machine=Machine(name=machine_name, flake=Flake(str(base_dir))),
        generator_name=None,
        regenerate=regenerate,
        include_previous_values=include_previous_values,
    )


def _generate_vars_for_machine(
    machine: "Machine",
    generators: list[Generator],
    all_prompt_values: dict[str, dict[str, str]],
    no_sandbox: bool = False,
) -> bool:
    for generator in generators:
        if check_can_migrate(machine, generator):
            migrate_files(machine, generator)
        else:
            execute_generator(
                machine=machine,
                generator=generator,
                secret_vars_store=machine.secret_vars_store,
                public_vars_store=machine.public_vars_store,
                prompt_values=all_prompt_values.get(generator.name, {}),
                no_sandbox=no_sandbox,
            )
    return True


@API.register
def generate_vars_for_machine(
    machine_name: str,
    generators: list[str],
    all_prompt_values: dict[str, dict[str, str]],
    base_dir: Path,
    no_sandbox: bool = False,
) -> bool:
    from clan_cli.machines.machines import Machine

    machine = Machine(name=machine_name, flake=Flake(str(base_dir)))
    generators_set = set(generators)
    generators_ = [g for g in machine.vars_generators() if g.name in generators_set]

    return _generate_vars_for_machine(
        machine=machine,
        generators=generators_,
        all_prompt_values=all_prompt_values,
        no_sandbox=no_sandbox,
    )


def generate_vars_for_machine_interactive(
    machine: "Machine",
    generator_name: str | None,
    regenerate: bool,
    no_sandbox: bool = False,
) -> bool:
    _generator = None
    if generator_name:
        for generator in machine.vars_generators():
            if generator.name == generator_name:
                _generator = generator
                break

    pub_healtcheck_msg = machine.public_vars_store.health_check(_generator)
    sec_healtcheck_msg = machine.secret_vars_store.health_check(_generator)

    if pub_healtcheck_msg or sec_healtcheck_msg:
        msg = f"Health check failed for machine {machine.name}:\n"
        if pub_healtcheck_msg:
            msg += f"Public vars store: {pub_healtcheck_msg}\n"
        if sec_healtcheck_msg:
            msg += f"Secret vars store: {sec_healtcheck_msg}"
        raise ClanError(msg)

    generators = get_closure(machine, generator_name, regenerate)
    if len(generators) == 0:
        return False
    all_prompt_values = {}
    for generator in generators:
        all_prompt_values[generator.name] = _ask_prompts(generator)
    return _generate_vars_for_machine(
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
) -> bool:
    was_regenerated = False
    for machine in machines:
        errors = []
        try:
            was_regenerated |= generate_vars_for_machine_interactive(
                machine, generator_name, regenerate, no_sandbox=no_sandbox
            )
        except Exception as exc:
            errors += [(machine, exc)]
        if len(errors) == 1:
            raise errors[0][1]
        if len(errors) > 1:
            msg = f"Failed to generate facts for {len(errors)} hosts:"
            for machine, error in errors:
                msg += f"\n{machine}: {error}"
            raise ClanError(msg) from errors[0][1]

    if not was_regenerated and len(machines) > 0:
        for machine in machines:
            machine.info("All vars are already up to date")

    return was_regenerated


def generate_command(args: argparse.Namespace) -> None:
    if args.flake is None:
        msg = "Could not find clan flake toplevel directory"
        raise ClanError(msg)

    machines: list[Machine] = list(list_machines(args.flake, args.option).values())

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
    args.flake.precache(
        [
            f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.generators.*.validationHash",
            f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.system.clan.deployment.file",
        ]
    )
    has_changed = generate_vars(
        machines, args.generator, args.regenerate, no_sandbox=args.no_sandbox
    )
    if has_changed:
        args.flake.invalidate_cache()


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

    parser.set_defaults(func=generate_command)
