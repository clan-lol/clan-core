import argparse
import importlib
import logging
import os
import shlex
import shutil
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from .cmd import Log, run
from .errors import ClanError
from .machines.machines import Machine
from .nix import nix_shell
from .secrets.modules import SecretStoreBase

log = logging.getLogger(__name__)


def flash_machine(
    machine: Machine, disks: dict[str, str], dry_run: bool, debug: bool
) -> None:
    secrets_module = importlib.import_module(machine.secrets_module)
    secret_store: SecretStoreBase = secrets_module.SecretStore(machine=machine)
    with TemporaryDirectory() as tmpdir_:
        tmpdir = Path(tmpdir_)
        upload_dir = machine.secrets_upload_directory

        if upload_dir.startswith("/"):
            local_dir = tmpdir / upload_dir[1:]
        else:
            local_dir = tmpdir / upload_dir

        local_dir.mkdir(parents=True)
        secret_store.upload(local_dir)
        disko_install = []

        if os.geteuid() != 0:
            if shutil.which("sudo") is None:
                raise ClanError(
                    "sudo is required to run disko-install as a non-root user"
                )
            disko_install.append("sudo")

        disko_install.append("disko-install")
        if dry_run:
            disko_install.append("--dry-run")
        if debug:
            disko_install.append("--debug")
        for name, device in disks.items():
            disko_install.extend(["--disk", name, device])

        disko_install.extend(["--extra-files", str(local_dir), upload_dir])
        disko_install.extend(["--flake", str(machine.flake) + "#" + machine.name])

        cmd = nix_shell(
            ["nixpkgs#disko"],
            disko_install,
        )
        print("$", " ".join(map(shlex.quote, cmd)))
        run(cmd, log=Log.BOTH, error_msg=f"Failed to flash {machine}")


@dataclass
class FlashOptions:
    flake: Path
    machine: str
    disks: dict[str, str]
    dry_run: bool
    confirm: bool
    debug: bool


class AppendDiskAction(argparse.Action):
    def __init__(self, option_strings: str, dest: str, **kwargs: Any) -> None:
        super().__init__(option_strings, dest, **kwargs)

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[str] | None,
        option_string: str | None = None,
    ) -> None:
        disks = getattr(namespace, self.dest)
        assert isinstance(values, list), "values must be a list"
        disks[values[0]] = values[1]


def flash_command(args: argparse.Namespace) -> None:
    opts = FlashOptions(
        flake=args.flake,
        machine=args.machine,
        disks=args.disk,
        dry_run=args.dry_run,
        confirm=not args.yes,
        debug=args.debug,
    )
    machine = Machine(opts.machine, flake=opts.flake)
    if opts.confirm and not opts.dry_run:
        disk_str = ", ".join(f"{name}={device}" for name, device in opts.disks.items())
        ask = input(f"Install {machine.name} to {disk_str}? [y/N] ")
        if ask != "y":
            return
    flash_machine(machine, disks=opts.disks, dry_run=opts.dry_run, debug=opts.debug)


def register_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machine",
        type=str,
        help="machine to install",
    )
    parser.add_argument(
        "--disk",
        type=str,
        nargs=2,
        metavar=("name", "value"),
        action=AppendDiskAction,
        help="device to flash to",
        default={},
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="do not ask for confirmation",
        default=False,
    )
    parser.add_argument(
        "--dry-run",
        help="Only build the system, don't flash it",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "--debug",
        help="Print debug information",
        default=False,
        action="store_true",
    )
    parser.set_defaults(func=flash_command)
