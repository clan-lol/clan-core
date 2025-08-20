import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Literal

from clan_cli.facts.generate import generate_facts
from clan_cli.vars.upload import populate_secret_vars

from clan_lib.api import API
from clan_lib.cmd import Log, RunOpts, cmd_with_root, run
from clan_lib.dirs import clan_core_flake
from clan_lib.errors import ClanError
from clan_lib.flake.flake import Flake
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_shell
from clan_lib.vars.generate import run_generators

from .automount import pause_automounting
from .list import list_keymaps, list_languages

log = logging.getLogger(__name__)


@dataclass
class SystemConfig:
    keymap: str = field(default="en")
    language: str = field(
        default="en_US.UTF-8"
    )  # Leave this default, or implement virtual scrolling for the 400+ options in the UI.
    ssh_keys_path: list[str] | None = field(default=None)


@dataclass
class Disk:
    name: str
    device: str


installer_machine = Machine(name="flash-installer", flake=Flake(str(clan_core_flake())))


# TODO: unify this with machine install
@API.register
def run_machine_flash(
    disks: list[Disk],
    system_config: SystemConfig,
    # Optional parameters
    machine: Machine = installer_machine,
    mode: Literal["format", "mount"] = "format",
    dry_run: bool = False,
    write_efi_boot_entries: bool = False,
    debug: bool = False,
    extra_args: list[str] | None = None,
    graphical: bool = False,
) -> None:
    """Flash a machine with the given configuration.
    Args:
        machine: The Machine instance to flash.
        mode: The mode to use for flashing (e.g., "install", "reinstall
        disks: List of Disk instances representing the disks to flash.
        system_config: SystemConfig instance containing language, keymap, and SSH keys.
        dry_run: If True, perform a dry run without making changes.
        write_efi_boot_entries: If True, write EFI boot entries.
        debug: If True, enable debug mode.
        extra_args: Additional arguments to pass to the disko-install command.
        graphical: If True, run the command in graphical mode.
    Raises:
        ClanError: If the language or keymap is invalid, or if there are issues with
            reading SSH keys, or if disko-install fails.
    """
    devices = [Path(disk.device) for disk in disks]
    with pause_automounting(devices, machine, request_graphical=graphical):
        if extra_args is None:
            extra_args = []
        system_config_nix: dict[str, Any] = {}

        generate_facts([machine])
        run_generators([machine], generators=None, full_closure=False)

        if system_config.language:
            if system_config.language not in list_languages():
                msg = (
                    f"Language '{system_config.language}' is not a valid language. "
                    f"Run 'clan flash list languages' to see a list of possible languages."
                )
                raise ClanError(msg)
            system_config_nix["i18n"] = {"defaultLocale": system_config.language}

        if system_config.keymap:
            if system_config.keymap not in list_keymaps():
                msg = (
                    f"Keymap '{system_config.keymap}' is not a valid keymap. "
                    f"Run 'clan flash list keymaps' to see a list of possible keymaps."
                )
                raise ClanError(msg)
            system_config_nix["console"] = {"keyMap": system_config.keymap}
            system_config_nix["services"] = {
                "xserver": {"xkb": {"layout": system_config.keymap}}
            }

        if system_config.ssh_keys_path:
            root_keys = []
            for key_path in (Path(x) for x in system_config.ssh_keys_path):
                try:
                    root_keys.append(key_path.read_text())
                except OSError as e:
                    msg = f"Cannot read SSH public key file: {key_path}: {e}"
                    raise ClanError(msg) from e
            system_config_nix["users"] = {
                "users": {"root": {"openssh": {"authorizedKeys": {"keys": root_keys}}}}
            }

        from clan_cli.vars.generator import Generator

        for generator in Generator.get_machine_generators(machine.name, machine.flake):
            for file in generator.files:
                if file.needed_for == "partitioning":
                    msg = f"Partitioning time secrets are not supported with `clan flash write`: clan.core.vars.generators.{generator.name}.files.{file.name}"
                    raise ClanError(msg)

        with TemporaryDirectory(prefix="disko-install-") as _tmpdir:
            tmpdir = Path(_tmpdir)
            upload_dir = machine.secrets_upload_directory

            if upload_dir.startswith("/"):
                local_dir = tmpdir / upload_dir[1:]
            else:
                local_dir = tmpdir / upload_dir

            local_dir.mkdir(parents=True)
            machine.secret_facts_store.upload(local_dir)
            populate_secret_vars(machine, local_dir)
            disko_install = []

            if os.geteuid() != 0:
                wrapper = " ".join(
                    [
                        "disko_install=$(command -v disko-install);",
                        "exec",
                        *cmd_with_root(['"$disko_install" "$@"'], graphical=graphical),
                    ]
                )
                disko_install.extend(["bash", "-c", wrapper])

            disko_install.append("disko-install")
            if write_efi_boot_entries:
                disko_install.append("--write-efi-boot-entries")
            if dry_run:
                disko_install.append("--dry-run")
            if debug:
                disko_install.append("--debug")
            for disk in disks:
                disko_install.extend(["--disk", disk.name, disk.device])

                log.info("Will flash disk %s: %s", disk.name, disk.device)

            disko_install.extend(["--extra-files", str(local_dir), upload_dir])
            disko_install.extend(["--flake", str(machine.flake) + "#" + machine.name])
            disko_install.extend(["--mode", str(mode)])
            disko_install.extend(
                [
                    "--system-config",
                    json.dumps(system_config_nix),
                ]
            )
            disko_install.extend(["--option", "dry-run", "true"])
            disko_install.extend(extra_args)

            cmd = nix_shell(
                ["disko"],
                disko_install,
            )
            run(
                cmd,
                RunOpts(
                    log=Log.BOTH,
                    error_msg=f"Failed to flash {machine}",
                    needs_user_terminal=True,
                ),
            )
