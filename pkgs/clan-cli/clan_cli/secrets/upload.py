import argparse
import logging
import types
from importlib.machinery import SourceFileLoader
from pathlib import Path
from tempfile import TemporaryDirectory

from ..cmd import Log, run
from ..machines.machines import Machine
from ..nix import nix_shell

log = logging.getLogger(__name__)


def upload_secrets(machine: Machine) -> None:
    # load secrets module from file
    loader = SourceFileLoader("secret_module", machine.secrets_module)
    secrets_module = types.ModuleType(loader.name)
    loader.exec_module(secrets_module)
    secret_store = secrets_module.SecretStore(machine=machine)

    update_check = getattr(secret_store, "update_check", None)
    if callable(update_check):
        if update_check():
            log.info("Secrets already up to date")
            return
    with TemporaryDirectory() as tempdir:
        secrets = []
        for service in machine.secrets_data:
            for secret in machine.secrets_data[service]["secrets"]:
                secrets.append((service, secret))
        secret_store.upload(Path(tempdir), secrets)
        host = machine.host

        ssh_cmd = host.ssh_cmd()
        run(
            nix_shell(
                ["nixpkgs#rsync"],
                [
                    "rsync",
                    "-e",
                    " ".join(["ssh"] + ssh_cmd[2:]),
                    "-az",
                    "--delete",
                    f"{tempdir!s}/",
                    f"{host.user}@{host.host}:{machine.secrets_upload_directory}/",
                ],
            ),
            log=Log.BOTH,
        )


def upload_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake_dir=args.flake)
    upload_secrets(machine)


def register_upload_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        help="The machine to upload secrets to",
    )
    parser.set_defaults(func=upload_command)
