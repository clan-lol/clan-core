import argparse
import importlib
import logging
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from .machines.machines import Machine
from .secrets.generate import generate_secrets

log = logging.getLogger(__name__)


def flash_machine(machine: Machine, device: str | None = None) -> None:
    secrets_module = importlib.import_module(machine.secrets_module)
    secret_store = secrets_module.SecretStore(machine=machine)

    generate_secrets(machine)

    with TemporaryDirectory() as tmpdir_:
        tmpdir = Path(tmpdir_)
        upload_dir_ = machine.secrets_upload_directory

        if upload_dir_.startswith("/"):
            upload_dir_ = upload_dir_[1:]
        upload_dir = tmpdir / upload_dir_
        upload_dir.mkdir(parents=True)
        secret_store.upload(upload_dir)

        fs_image = machine.build_nix("config.system.clan.iso")
        print(fs_image)


@dataclass
class FlashOptions:
    flake: Path
    machine: str
    device: str | None


def flash_command(args: argparse.Namespace) -> None:
    opts = FlashOptions(
        flake=args.flake,
        machine=args.machine,
        device=args.device,
    )
    machine = Machine(opts.machine, flake=opts.flake)
    flash_machine(machine, device=opts.device)


def register_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        type=str,
        help="machine to install",
    )
    parser.add_argument(
        "--device",
        type=str,
        help="device to flash the system to",
    )
    parser.set_defaults(func=flash_command)
