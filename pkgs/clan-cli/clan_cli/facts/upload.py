import argparse
import importlib
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from ..cmd import Log, run
from ..completions import add_dynamic_completer, complete_machines
from ..machines.machines import Machine
from ..nix import run_cmd

log = logging.getLogger(__name__)


def upload_secrets(machine: Machine) -> None:
    secret_facts_module = importlib.import_module(machine.secret_facts_module)
    secret_facts_store = secret_facts_module.SecretStore(machine=machine)

    if secret_facts_store.update_check():
        log.info("Secrets already up to date")
        return
    with TemporaryDirectory() as tempdir:
        secret_facts_store.upload(Path(tempdir))
        host = machine.target_host

        ssh_cmd = host.ssh_cmd()
        run(
            run_cmd(
                ["rsync"],
                [
                    "rsync",
                    "-e",
                    " ".join(["ssh"] + ssh_cmd[2:]),
                    "-az",
                    "--delete",
                    "--chown=root:root",
                    "--chmod=D700,F600",
                    f"{tempdir!s}/",
                    f"{host.user}@{host.host}:{machine.secrets_upload_directory}/",
                ],
            ),
            log=Log.BOTH,
        )


def upload_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)
    upload_secrets(machine)


def register_upload_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machine",
        help="The machine to upload secrets to",
    )
    add_dynamic_completer(machines_parser, complete_machines)

    parser.set_defaults(func=upload_command)
