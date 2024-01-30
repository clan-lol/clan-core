import argparse
import importlib
import logging
import os
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from clan_cli.cmd import run

from ..errors import ClanError
from ..machines.machines import Machine
from ..nix import nix_shell

log = logging.getLogger(__name__)


def generate_secrets(machine: Machine) -> None:
    secrets_module = importlib.import_module(machine.secrets_module)
    secret_store = secrets_module.SecretStore(machine=machine)

    with TemporaryDirectory() as d:
        for service in machine.secrets_data:
            print(service)
            tmpdir = Path(d) / service
            # check if all secrets exist and generate them if at least one is missing
            needs_regeneration = any(
                not secret_store.exists(service, secret)
                for secret in machine.secrets_data[service]["secrets"]
            ) or any(
                not (machine.flake / fact).exists()
                for fact in machine.secrets_data[service]["facts"].values()
            )
            for fact in machine.secrets_data[service]["facts"].values():
                if not (machine.flake / fact).exists():
                    print(f"fact {fact} is missing")
            if needs_regeneration:
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
                # store secrets
                for secret in machine.secrets_data[service]["secrets"]:
                    secret_file = secrets_dir / secret
                    if not secret_file.is_file():
                        msg = f"did not generate a file for '{secret}' when running the following command:\n"
                        msg += machine.secrets_data[service]["generator"]
                        raise ClanError(msg)
                    secret_store.set(service, secret, secret_file.read_text())
                # store facts
                for name, fact_path in machine.secrets_data[service]["facts"].items():
                    fact_file = facts_dir / name
                    if not fact_file.is_file():
                        msg = f"did not generate a file for '{name}' when running the following command:\n"
                        msg += machine.secrets_data[service]["generator"]
                        raise ClanError(msg)
                    fact_path = machine.flake / fact_path
                    fact_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(fact_file, fact_path)

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
