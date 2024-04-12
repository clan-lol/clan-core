import argparse
import importlib
import logging
import os
import subprocess
from collections.abc import Callable
from pathlib import Path
from tempfile import TemporaryDirectory

from clan_cli.cmd import run

from ..errors import ClanError
from ..git import commit_files
from ..machines.machines import Machine
from ..nix import nix_shell
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
    return proc.stdout


def generate_service_facts(
    machine: Machine,
    service: str,
    secret_facts_store: SecretStoreBase,
    public_facts_store: FactStoreBase,
    tmpdir: Path,
    prompt: Callable[[str], str],
) -> bool:
    service_dir = tmpdir / service
    # check if all secrets exist and generate them if at least one is missing
    needs_regeneration = not check_secrets(machine, service=service)
    log.debug(f"{service} needs_regeneration: {needs_regeneration}")
    if not needs_regeneration:
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
            prompt_value = prompt(machine.facts_data[service]["generator"]["prompt"])
            env["prompt_value"] = prompt_value
    # fmt: off
    cmd = nix_shell(
        [
            "nixpkgs#bash",
            "nixpkgs#bubblewrap",
        ],
        [
            "bwrap",
            "--ro-bind", "/nix/store", "/nix/store",
            "--tmpfs",  "/usr/lib/systemd",
            "--dev", "/dev",
            "--bind", str(facts_dir), str(facts_dir),
            "--bind", str(secrets_dir), str(secrets_dir),
            "--unshare-all",
            "--unshare-user",
            "--uid", "1000",
            "--",
            "bash", "-c", generator
        ],
    )
    # fmt: on
    run(
        cmd,
        env=env,
    )
    files_to_commit = []
    # store secrets
    for secret in machine.facts_data[service]["secret"]:
        if isinstance(secret, str):
            # TODO: This is the old NixOS module, can be dropped everyone has updated.
            secret_name = secret
            groups = []
        else:
            secret_name = secret["name"]
            groups = secret.get("groups", [])

        secret_file = secrets_dir / secret_name
        if not secret_file.is_file():
            msg = f"did not generate a file for '{secret_name}' when running the following command:\n"
            msg += generator
            raise ClanError(msg)
        secret_path = secret_facts_store.set(
            service, secret_name, secret_file.read_bytes(), groups
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


def generate_facts(
    machine: Machine,
    prompt: None | Callable[[str], str] = None,
) -> bool:
    secret_facts_module = importlib.import_module(machine.secret_facts_module)
    secret_facts_store = secret_facts_module.SecretStore(machine=machine)

    public_facts_module = importlib.import_module(machine.public_facts_module)
    public_facts_store = public_facts_module.FactStore(machine=machine)

    if prompt is None:

        def prompt_func(text: str) -> str:
            print(f"{text}: ")
            return read_multiline_input()

        prompt = prompt_func

    was_regenerated = False
    with TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for service in machine.facts_data:
            was_regenerated |= generate_service_facts(
                machine=machine,
                service=service,
                secret_facts_store=secret_facts_store,
                public_facts_store=public_facts_store,
                tmpdir=tmpdir,
                prompt=prompt,
            )

    if was_regenerated:
        # flush caches to make sure the new secrets are available in evaluation
        machine.flush_caches()
    else:
        print("All secrets and facts are already up to date")
    return was_regenerated


def generate_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)
    generate_facts(machine)


def register_generate_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to generate facts for",
    )
    parser.set_defaults(func=generate_command)
