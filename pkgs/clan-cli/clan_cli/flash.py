import argparse
import importlib
import json
import logging
import os
import shutil
import textwrap
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from .clan_uri import FlakeId
from .cmd import Log, run
from .completions import add_dynamic_completer, complete_machines
from .errors import ClanError
from .facts.secret_modules import SecretStoreBase
from .machines.machines import Machine
from .nix import nix_shell

log = logging.getLogger(__name__)


def flash_machine(
    machine: Machine,
    *,
    mode: str,
    disks: dict[str, str],
    system_config: dict[str, Any],
    dry_run: bool,
    write_efi_boot_entries: bool,
    debug: bool,
    extra_args: list[str] = [],
) -> None:
    secret_facts_module = importlib.import_module(machine.secret_facts_module)
    secret_facts_store: SecretStoreBase = secret_facts_module.SecretStore(
        machine=machine
    )
    with TemporaryDirectory() as tmpdir_:
        tmpdir = Path(tmpdir_)
        upload_dir = machine.secrets_upload_directory

        if upload_dir.startswith("/"):
            local_dir = tmpdir / upload_dir[1:]
        else:
            local_dir = tmpdir / upload_dir

        local_dir.mkdir(parents=True)
        secret_facts_store.upload(local_dir)
        disko_install = []

        if os.geteuid() != 0:
            if shutil.which("sudo") is None:
                raise ClanError(
                    "sudo is required to run disko-install as a non-root user"
                )
            disko_install.append("sudo")

        disko_install.append("disko-install")
        if write_efi_boot_entries:
            disko_install.append("--write-efi-boot-entries")
        if dry_run:
            disko_install.append("--dry-run")
        if debug:
            disko_install.append("--debug")
        for name, device in disks.items():
            disko_install.extend(["--disk", name, device])

        disko_install.extend(["--extra-files", str(local_dir), upload_dir])
        disko_install.extend(["--flake", str(machine.flake) + "#" + machine.name])
        disko_install.extend(["--mode", str(mode)])
        disko_install.extend(
            [
                "--system-config",
                json.dumps(system_config),
            ]
        )
        disko_install.extend(["--option", "dry-run", "true"])
        disko_install.extend(extra_args)

        cmd = nix_shell(
            ["nixpkgs#disko"],
            disko_install,
        )
        run(cmd, log=Log.BOTH, error_msg=f"Failed to flash {machine}")


@dataclass
class FlashOptions:
    flake: FlakeId
    machine: str
    disks: dict[str, str]
    ssh_keys_path: list[Path]
    dry_run: bool
    confirm: bool
    debug: bool
    mode: str
    language: str
    keymap: str
    write_efi_boot_entries: bool
    nix_options: list[str]


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
        ssh_keys_path=args.ssh_pubkey,
        dry_run=args.dry_run,
        confirm=not args.yes,
        debug=args.debug,
        mode=args.mode,
        language=args.language,
        keymap=args.keymap,
        write_efi_boot_entries=args.write_efi_boot_entries,
        nix_options=args.option,
    )

    machine = Machine(opts.machine, flake=opts.flake)
    if opts.confirm and not opts.dry_run:
        disk_str = ", ".join(f"{name}={device}" for name, device in opts.disks.items())
        msg = f"Install {machine.name}"
        if disk_str != "":
            msg += f" to {disk_str}"
        msg += "? [y/N] "
        ask = input(msg)
        if ask != "y":
            return

    extra_config: dict[str, Any] = {}
    if opts.ssh_keys_path:
        root_keys = []
        for key_path in opts.ssh_keys_path:
            try:
                root_keys.append(key_path.read_text())
            except OSError as e:
                raise ClanError(f"Cannot read SSH public key file: {key_path}: {e}")
        extra_config["users"] = {
            "users": {"root": {"openssh": {"authorizedKeys": {"keys": root_keys}}}}
        }
    if opts.keymap:
        extra_config["console"] = {"keyMap": opts.keymap}

    if opts.language:
        extra_config["i18n"] = {"defaultLocale": opts.language}

    flash_machine(
        machine,
        mode=opts.mode,
        disks=opts.disks,
        system_config=extra_config,
        dry_run=opts.dry_run,
        debug=opts.debug,
        write_efi_boot_entries=opts.write_efi_boot_entries,
        extra_args=opts.nix_options,
    )


def register_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machine",
        type=str,
        help="machine to install",
    )
    add_dynamic_completer(machines_parser, complete_machines)

    parser.add_argument(
        "--disk",
        type=str,
        nargs=2,
        metavar=("name", "value"),
        action=AppendDiskAction,
        help="device to flash to",
        default={},
    )
    mode_help = textwrap.dedent(
        """\
        Specify the mode of operation. Valid modes are: format, mount."
        Format will format the disk before installing.
        Mount will mount the disk before installing.
        Mount is useful for updating an existing system without losing data.
        """
    )
    parser.add_argument(
        "--mode",
        type=str,
        help=mode_help,
        choices=["format", "mount"],
        default="format",
    )
    parser.add_argument(
        "--ssh-pubkey",
        type=Path,
        action="append",
        default=[],
        help="ssh pubkey file to add to the root user. Can be used multiple times",
    )
    parser.add_argument(
        "--language",
        type=str,
        help="system language",
    )
    parser.add_argument(
        "--keymap",
        type=str,
        help="system keymap",
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
        "--write-efi-boot-entries",
        help=textwrap.dedent(
            """
          Write EFI boot entries to the NVRAM of the system for the installed system.
          Specify this option if you plan to boot from this disk on the current machine,
          but not if you plan to move the disk to another machine.
        """
        ).strip(),
        default=False,
        action="store_true",
    )
    parser.set_defaults(func=flash_command)
