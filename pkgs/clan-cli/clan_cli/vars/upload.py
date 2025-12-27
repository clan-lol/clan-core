import argparse
from pathlib import Path

from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_lib.flake import require_flake
from clan_lib.machines.machines import Machine
from clan_lib.network.network import get_best_remote
from clan_lib.vars.upload import populate_secret_vars, upload_secret_vars


def upload_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    machine = Machine(name=args.machine, flake=flake)
    directory = None
    if args.directory:
        directory = Path(args.directory)
        directory.mkdir(parents=True, exist_ok=True)
        populate_secret_vars(machine, directory)
        return

    # Use get_best_remote to handle networking
    with (
        get_best_remote(machine) as remote,
        remote.host_connection() as host,
        host.become_root() as host,
    ):
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
