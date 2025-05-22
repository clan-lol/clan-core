import argparse
import logging
from pathlib import Path

from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_cli.machines.machines import Machine
from clan_lib.ssh.remote import Remote

log = logging.getLogger(__name__)


def upload_secret_vars(machine: Machine, host: Remote) -> None:
    machine.secret_vars_store.upload(host, phases=["activation", "users", "services"])


def populate_secret_vars(machine: Machine, directory: Path) -> None:
    machine.secret_vars_store.populate_dir(
        directory, phases=["activation", "users", "services"]
    )


def upload_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)
    directory = None
    if args.directory:
        directory = Path(args.directory)
        directory.mkdir(parents=True, exist_ok=True)
        populate_secret_vars(machine, directory)
        return

    host = machine.target_host()
    upload_secret_vars(machine, host)


def register_upload_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machine",
        help="The machine to upload secrets to",
    )
    add_dynamic_completer(machines_parser, complete_machines)

    parser.add_argument(
        "--directory",
        help="If provided, secrets will be copied into this directory instead of the remote server",
    )
    parser.set_defaults(func=upload_command)
