import argparse
import logging
import os
import sys
import traceback
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

from clan_lib.cmd import RunOpts, run
from clan_lib.errors import ClanError
from clan_lib.flake import require_flake
from clan_lib.git import commit_files
from clan_lib.machines.list import list_full_machines
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_shell

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_services_for_machine,
)

from .check import check_secrets
from .public_modules import FactStoreBase
from .secret_modules import SecretStoreBase

log = logging.getLogger(__name__)


def read_multiline_input(prompt: str = "Finish with Ctrl-D") -> str:
    """Read multi-line input from stdin."""
    print(prompt, flush=True)
    proc = run(["cat"], RunOpts(check=False))
    log.info("Input received. Processing...")
    return proc.stdout.rstrip(os.linesep).rstrip()


def bubblewrap_cmd(generator: str, facts_dir: Path, secrets_dir: Path) -> list[str]:
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
            "--dev", "/dev",
            # not allowed to bind procfs in some sandboxes
            "--bind", str(facts_dir), str(facts_dir),
            "--bind", str(secrets_dir), str(secrets_dir),
            "--chdir", "/",
            # Doesn't work in our CI?
            #"--proc", "/proc",
            #"--hostname", "facts",
            "--bind", "/proc", "/proc",
            "--uid", "1000",
            "--gid", "1000",
            "--",
            "bash", "-c", generator,
        ],
    )
    # fmt: on


def generate_service_facts(
    machine: Machine,
    service: str,
    regenerate: bool,
    secret_facts_store: SecretStoreBase,
    public_facts_store: FactStoreBase,
    tmpdir: Path,
    prompt: Callable[[str, str], str],
) -> bool:
    service_dir = tmpdir / service
    # check if all secrets exist and generate them if at least one is missing
    needs_regeneration = not check_secrets(machine, service=service)
    machine.debug(f"{service} needs_regeneration: {needs_regeneration}")
    if not (needs_regeneration or regenerate):
        return False
    if not isinstance(machine.flake, Path):
        msg = f"flake is not a Path: {machine.flake}"
        msg += "fact/secret generation is only supported for local flakes"

    env = os.environ.copy()
    facts_dir = service_dir / "facts"
    facts_dir.mkdir(parents=True)
    env["facts"] = str(facts_dir)
    secrets_dir = service_dir / "secrets"
    secrets_dir.mkdir(parents=True)
    env["secrets"] = str(secrets_dir)
    # compatibility for old outputs.nix users
    if isinstance(machine.facts_data[service]["generator"], str):
        generator = machine.facts_data[service]["generator"]
    else:
        generator = machine.facts_data[service]["generator"]["finalScript"]
        if machine.facts_data[service]["generator"]["prompt"]:
            prompt_value = prompt(
                service,
                machine.facts_data[service]["generator"]["prompt"],
            )
            env["prompt_value"] = prompt_value
    from clan_lib import bwrap

    if sys.platform == "linux" and bwrap.bubblewrap_works():
        cmd = bubblewrap_cmd(generator, facts_dir, secrets_dir)
    else:
        cmd = ["bash", "-c", generator]
    run(
        cmd,
        RunOpts(env=env),
    )
    files_to_commit = []
    # store secrets
    for secret_name, secret in machine.facts_data[service]["secret"].items():
        groups = secret.get("groups", [])

        secret_file = secrets_dir / secret_name
        if not secret_file.is_file():
            msg = f"did not generate a file for '{secret_name}' when running the following command:\n"
            msg += generator
            raise ClanError(msg)
        secret_path = secret_facts_store.set(
            service,
            secret_name,
            secret_file.read_bytes(),
            groups,
        )
        if secret_path:
            files_to_commit.append(secret_path)

    # store facts
    for name in machine.facts_data[service]["public"]:
        fact_file = facts_dir / name
        if not fact_file.is_file():
            msg = f"did not generate a file for '{name}' when running the following command:\n"
            msg += machine.facts_data[service]["generator"]
            raise ClanError(msg)
        fact_file = public_facts_store.set(service, name, fact_file.read_bytes())
        if fact_file:
            files_to_commit.append(fact_file)
    commit_files(
        files_to_commit,
        machine.flake_dir,
        f"Update facts/secrets for service {service} in machine {machine.name}",
    )
    return True


def prompt_func(_service: str, text: str) -> str:
    print(f"{text}: ")
    return read_multiline_input()


def _generate_facts_for_machine(
    machine: Machine,
    service: str | None,
    regenerate: bool,
    tmpdir: Path,
    prompt: Callable[[str, str], str] = prompt_func,
) -> bool:
    local_temp = tmpdir / machine.name
    local_temp.mkdir()

    machine_updated = False

    if service and service not in machine.facts_data:
        services = list(machine.facts_data.keys())
        msg = f"Could not find service with name: {service}. The following services are available: {services}"
        raise ClanError(msg)

    if service:
        machine_service_facts = {service: machine.facts_data[service]}
    else:
        machine_service_facts = machine.facts_data

    for service in machine_service_facts:
        machine_updated |= generate_service_facts(
            machine=machine,
            service=service,
            regenerate=regenerate,
            secret_facts_store=machine.secret_facts_store,
            public_facts_store=machine.public_facts_store,
            tmpdir=local_temp,
            prompt=prompt,
        )
    if machine_updated:
        # flush caches to make sure the new secrets are available in evaluation
        machine.flush_caches()
    return machine_updated


def generate_facts(
    machines: list[Machine],
    service: str | None = None,
    regenerate: bool = False,
    prompt: Callable[[str, str], str] = prompt_func,
) -> bool:
    was_regenerated = False
    with TemporaryDirectory(prefix="facts-generate-") as _tmpdir:
        tmpdir = Path(_tmpdir).resolve()

        for machine in machines:
            errors = 0
            try:
                was_regenerated |= _generate_facts_for_machine(
                    machine,
                    service,
                    regenerate,
                    tmpdir,
                    prompt,
                )
            except (OSError, ClanError) as e:
                machine.error(f"Failed to generate facts: {e}")
                traceback.print_exc()
                errors += 1
            if errors > 0:
                msg = (
                    f"Failed to generate facts for {errors} hosts. Check the logs above"
                )
                raise ClanError(msg)

    if not was_regenerated and len(machines) > 0:
        log.info("All secrets and facts are already up to date")
    return was_regenerated


def generate_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machines: list[Machine] = list(list_full_machines(flake).values())
    if len(args.machines) > 0:
        machines = list(
            filter(
                lambda m: m.name in args.machines,
                machines,
            ),
        )
    generate_facts(machines, args.service, args.regenerate)


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
        action=argparse.BooleanOptionalAction,
        help="whether to regenerate facts for the specified machine",
        default=None,
    )
    parser.set_defaults(func=generate_command)
