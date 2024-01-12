import argparse
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

from ..cmd import Log, run
from ..machines.machines import Machine
from ..nix import nix_shell

log = logging.getLogger(__name__)


def upload_secrets(machine: Machine) -> None:
    with TemporaryDirectory() as tempdir_:
        tempdir = Path(tempdir_)
        should_upload = machine.run_upload_secrets(tempdir)

        if should_upload:
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
