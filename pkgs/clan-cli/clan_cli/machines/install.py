import argparse
import subprocess
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from ..machines.machines import Machine
from ..nix import nix_shell
from ..secrets.generate import generate_secrets


def install_nixos(machine: Machine, kexec: str | None = None) -> None:
    h = machine.host
    target_host = f"{h.user or 'root'}@{h.host}"

    flake_attr = h.meta.get("flake_attr", "")

    generate_secrets(machine)

    with TemporaryDirectory() as tmpdir_:
        tmpdir = Path(tmpdir_)
        upload_dir = machine.secrets_upload_directory

        if upload_dir.startswith("/"):
            upload_dir = upload_dir[1:]
        upload_dir = tmpdir / upload_dir
        upload_dir.mkdir(parents=True)
        machine.run_upload_secrets(upload_dir)

        cmd = [
            "nixos-anywhere",
            "-f",
            f"{machine.flake_dir}#{flake_attr}",
            "-t",
            "--no-reboot",
            "--extra-files",
            str(tmpdir),
        ]
        if kexec:
            cmd += ["--kexec", kexec]
        cmd.append(target_host)

        subprocess.run(
            nix_shell(
                ["nixpkgs#nixos-anywhere"],
                cmd,
            ),
            check=True,
        )


@dataclass
class InstallOptions:
    flake: Path
    machine: str
    target_host: str
    kexec: str | None


def install_command(args: argparse.Namespace) -> None:
    opts = InstallOptions(
        flake=args.flake,
        machine=args.machine,
        target_host=args.target_host,
        kexec=args.kexec,
    )
    machine = Machine(opts.machine, flake_dir=opts.flake)
    machine.deployment_address = opts.target_host

    install_nixos(machine, kexec=opts.kexec)


def register_install_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--kexec",
        type=str,
        help="use another kexec tarball to bootstrap NixOS",
    )
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
    parser.set_defaults(func=install_command)
