import argparse
import importlib
import logging
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from ..cmd import Log, run
from ..machines.machines import Machine
from ..nix import nix_shell
from ..secrets.generate import generate_secrets

log = logging.getLogger(__name__)


def install_nixos(machine: Machine, kexec: str | None = None) -> None:
    secrets_module = importlib.import_module(machine.secrets_module)
    log.info(f"installing {machine.name}")
    log.info(f"using secret store: {secrets_module.SecretStore}")
    secret_store = secrets_module.SecretStore(machine=machine)

    h = machine.host
    target_host = f"{h.user or 'root'}@{h.host}"
    log.info(f"target host: {target_host}")

    flake_attr = h.meta.get("flake_attr", "")

    generate_secrets(machine)

    with TemporaryDirectory() as tmpdir_:
        tmpdir = Path(tmpdir_)
        upload_dir_ = machine.secrets_upload_directory

        if upload_dir_.startswith("/"):
            upload_dir_ = upload_dir_[1:]
        upload_dir = tmpdir / upload_dir_
        upload_dir.mkdir(parents=True)
        secret_store.upload(upload_dir)

        cmd = [
            "nixos-anywhere",
            "-f",
            f"{machine.flake}#{flake_attr}",
            "-t",
            "--no-reboot",
            "--extra-files",
            str(tmpdir),
        ]
        if kexec:
            cmd += ["--kexec", kexec]
        cmd.append(target_host)

        run(
            nix_shell(
                ["nixpkgs#nixos-anywhere"],
                cmd,
            ),
            log=Log.BOTH,
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
    machine = Machine(opts.machine, flake=opts.flake)
    machine.target_host = opts.target_host

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
