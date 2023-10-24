import argparse
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from ..dirs import get_flake_path
from ..machines.machines import Machine
from ..nix import nix_shell
from ..secrets.generate import generate_secrets


def install_nixos(machine: Machine) -> None:
    h = machine.host
    target_host = f"{h.user or 'root'}@{h.host}"

    flake_attr = h.meta.get("flake_attr", "")

    generate_secrets(machine)

    with TemporaryDirectory() as tmpdir_:
        tmpdir = Path(tmpdir_)
        machine.run_upload_secrets(tmpdir / machine.secrets_upload_directory)

        subprocess.run(
            nix_shell(
                ["nixos-anywhere"],
                [
                    "nixos-anywhere",
                    "-f",
                    f"{machine.flake_dir}#{flake_attr}",
                    "-t",
                    "--no-reboot",
                    "--extra-files",
                    str(tmpdir),
                    target_host,
                ],
            ),
            check=True,
        )


def install_command(args: argparse.Namespace) -> None:
    machine = Machine(args.machine, flake_dir=get_flake_path(args.flake))
    machine.deployment_address = args.target_host

    install_nixos(machine)


def register_install_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        type=str,
        help="machine to install",
    )
    parser.add_argument(
        "target_host",
        type=str,
        help="ssh address to install to in the form of user@host:2222",
    )
    parser.add_argument(
        "flake",
        type=str,
        help="name of the flake to install machine from",
    )
    parser.set_defaults(func=install_command)
