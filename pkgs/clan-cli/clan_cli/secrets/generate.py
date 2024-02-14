import argparse
import importlib
import logging
import os
from pathlib import Path
from tempfile import TemporaryDirectory

from clan_cli.cmd import run

from ..errors import ClanError
from ..git import commit_files
from ..machines.machines import Machine
from ..nix import nix_shell
from .check import check_secrets

log = logging.getLogger(__name__)


def generate_secrets(machine: Machine) -> None:
    secrets_module = importlib.import_module(machine.secrets_module)
    secret_store = secrets_module.SecretStore(machine=machine)

    facts_module = importlib.import_module(machine.facts_module)
    fact_store = facts_module.FactStore(machine=machine)

    with TemporaryDirectory() as d:
        for service in machine.secrets_data:
            tmpdir = Path(d) / service
            # check if all secrets exist and generate them if at least one is missing
            needs_regeneration = not check_secrets(machine)
            log.debug(f"{service} needs_regeneration: {needs_regeneration}")
            if needs_regeneration:
                if not isinstance(machine.flake, Path):
                    msg = f"flake is not a Path: {machine.flake}"
                    msg += "fact/secret generation is only supported for local flakes"

                env = os.environ.copy()
                facts_dir = tmpdir / "facts"
                facts_dir.mkdir(parents=True)
                env["facts"] = str(facts_dir)
                secrets_dir = tmpdir / "secrets"
                secrets_dir.mkdir(parents=True)
                env["secrets"] = str(secrets_dir)
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
                        "bash", "-c", machine.secrets_data[service]["generator"]
                    ],
                )
                # fmt: on
                run(
                    cmd,
                    env=env,
                )
                files_to_commit = []
                # store secrets
                for secret in machine.secrets_data[service]["secrets"]:
                    secret_file = secrets_dir / secret
                    if not secret_file.is_file():
                        msg = f"did not generate a file for '{secret}' when running the following command:\n"
                        msg += machine.secrets_data[service]["generator"]
                        raise ClanError(msg)
                    secret_path = secret_store.set(
                        service, secret, secret_file.read_bytes()
                    )
                    if secret_path:
                        files_to_commit.append(secret_path)

                # store facts
                for name in machine.secrets_data[service]["facts"]:
                    fact_file = facts_dir / name
                    if not fact_file.is_file():
                        msg = f"did not generate a file for '{name}' when running the following command:\n"
                        msg += machine.secrets_data[service]["generator"]
                        raise ClanError(msg)
                    fact_file = fact_store.set(service, name, fact_file.read_bytes())
                    if fact_file:
                        files_to_commit.append(fact_file)
                commit_files(
                    files_to_commit,
                    machine.flake_dir,
                    f"Update facts/secrets for service {service} in machine {machine.name}",
                )

    print("successfully generated secrets")


def generate_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)
    generate_secrets(machine)


def register_generate_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to generate secrets for",
    )
    parser.set_defaults(func=generate_command)
