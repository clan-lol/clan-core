import argparse
import importlib
import logging
import os
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

from clan_cli.cmd import run

from ..completions import (
    add_dynamic_completer,
    complete_machines,
    complete_services_for_machine,
)
from ..errors import ClanError
from ..git import commit_files
from ..machines.inventory import get_all_machines, get_selected_machines
from ..machines.machines import Machine
from ..nix import run_cmd
from .check import check_secrets
from .public_modules import FactStoreBase
from .secret_modules import SecretStoreBase

log = logging.getLogger(__name__)


def read_multiline_input(prompt: str = "Finish with Ctrl-D") -> str:
    """
    Read multi-line input from stdin.
    """
    print(prompt, flush=True)
    proc = subprocess.run(["cat"], stdout=subprocess.PIPE, text=True)
    log.info("Input received. Processing...")
    return proc.stdout


def bubblewrap_cmd(generator: str, generator_dir: Path) -> list[str]:
    # fmt: off
    return run_cmd(
        [
            "bash",
            "bubblewrap",
        ],
        [
            "bwrap",
            "--ro-bind", "/nix/store", "/nix/store",
            "--tmpfs",  "/usr/lib/systemd",
            "--dev", "/dev",
            "--bind", str(generator_dir), str(generator_dir),
            "--unshare-all",
            "--unshare-user",
            "--uid", "1000",
            "--",
            "bash", "-c", generator
        ],
    )
    # fmt: on


def execute_generator(
    machine: Machine,
    generator_name: str,
    regenerate: bool,
    secret_vars_store: SecretStoreBase,
    public_vars_store: FactStoreBase,
    tmpdir: Path,
    prompt: Callable[[str], str],
) -> bool:
    generator_dir = tmpdir / generator_name
    # check if all secrets exist and generate them if at least one is missing
    needs_regeneration = not check_secrets(machine, generator_name=generator_name)
    log.debug(f"{generator_name} needs_regeneration: {needs_regeneration}")
    if not (needs_regeneration or regenerate):
        return False
    if not isinstance(machine.flake, Path):
        msg = f"flake is not a Path: {machine.flake}"
        msg += "fact/secret generation is only supported for local flakes"

    env = os.environ.copy()
    generator_dir.mkdir(parents=True)
    env["out"] = str(generator_dir)
    # compatibility for old outputs.nix users
    generator = machine.vars_generators[generator_name]["finalScript"]
    # if machine.vars_data[generator_name]["generator"]["prompt"]:
    #     prompt_value = prompt(machine.vars_data[generator_name]["generator"]["prompt"])
    #     env["prompt_value"] = prompt_value
    if sys.platform == "linux":
        cmd = bubblewrap_cmd(generator, generator_dir)
    else:
        cmd = ["bash", "-c", generator]
    run(
        cmd,
        env=env,
    )
    files_to_commit = []
    # store secrets
    files = machine.vars_generators[generator_name]["files"]
    for file_name, file in files.items():
        groups = machine.deployment["sops"]["defaultGroups"]

        secret_file = generator_dir / file_name
        if not secret_file.is_file():
            msg = f"did not generate a file for '{file_name}' when running the following command:\n"
            msg += generator
            raise ClanError(msg)
        if file["secret"]:
            file_path = secret_vars_store.set(
                generator_name, file_name, secret_file.read_bytes(), groups
            )
        else:
            file_path = public_vars_store.set(
                generator_name, file_name, secret_file.read_bytes()
            )
        if file_path:
            files_to_commit.append(file_path)
    commit_files(
        files_to_commit,
        machine.flake_dir,
        f"Update facts/secrets for service {generator_name} in machine {machine.name}",
    )
    return True


def prompt_func(text: str) -> str:
    print(f"{text}: ")
    return read_multiline_input()


def _generate_vars_for_machine(
    machine: Machine,
    generator_name: str | None,
    regenerate: bool,
    tmpdir: Path,
    prompt: Callable[[str], str] = prompt_func,
) -> bool:
    local_temp = tmpdir / machine.name
    local_temp.mkdir()
    secret_vars_module = importlib.import_module(machine.secret_vars_module)
    secret_vars_store = secret_vars_module.SecretStore(machine=machine)

    public_vars_module = importlib.import_module(machine.public_vars_module)
    public_vars_store = public_vars_module.FactStore(machine=machine)

    machine_updated = False

    if generator_name and generator_name not in machine.vars_generators:
        generators = list(machine.vars_generators.keys())
        raise ClanError(
            f"Could not find generator with name: {generator_name}. The following generators are available: {generators}"
        )

    if generator_name:
        machine_generator_facts = {
            generator_name: machine.vars_generators[generator_name]
        }
    else:
        machine_generator_facts = machine.vars_generators

    for generator_name in machine_generator_facts:
        machine_updated |= execute_generator(
            machine=machine,
            generator_name=generator_name,
            regenerate=regenerate,
            secret_vars_store=secret_vars_store,
            public_vars_store=public_vars_store,
            tmpdir=local_temp,
            prompt=prompt,
        )
    if machine_updated:
        # flush caches to make sure the new secrets are available in evaluation
        machine.flush_caches()
    return machine_updated


def generate_vars(
    machines: list[Machine],
    generator_name: str | None,
    regenerate: bool,
    prompt: Callable[[str], str] = prompt_func,
) -> bool:
    was_regenerated = False
    with TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)

        for machine in machines:
            errors = 0
            try:
                was_regenerated |= _generate_vars_for_machine(
                    machine, generator_name, regenerate, tmpdir, prompt
                )
            except Exception as exc:
                log.error(f"Failed to generate facts for {machine.name}: {exc}")
                errors += 1
            if errors > 0:
                raise ClanError(
                    f"Failed to generate facts for {errors} hosts. Check the logs above"
                )

    if not was_regenerated:
        print("All secrets and facts are already up to date")
    return was_regenerated


def generate_command(args: argparse.Namespace) -> None:
    if len(args.machines) == 0:
        machines = get_all_machines(args.flake, args.option)
    else:
        machines = get_selected_machines(args.flake, args.option, args.machines)
    generate_vars(machines, args.service, args.regenerate)


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
        "--service",
        type=str,
        help="service to generate facts for, if empty, generate facts for every service",
        default=None,
    )
    add_dynamic_completer(service_parser, complete_services_for_machine)

    parser.add_argument(
        "--regenerate",
        type=bool,
        action=argparse.BooleanOptionalAction,
        help="whether to regenerate facts for the specified machine",
        default=None,
    )
    parser.set_defaults(func=generate_command)
