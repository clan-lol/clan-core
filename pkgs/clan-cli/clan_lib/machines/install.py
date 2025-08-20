import logging
import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from time import time
from typing import Literal

from clan_cli.facts.generate import generate_facts
from clan_cli.machines.hardware import HardwareConfig

from clan_lib.api import API, message_queue
from clan_lib.cmd import Log, RunOpts, run
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_config, nix_shell
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.util import set_value_by_path
from clan_lib.ssh.create import create_secret_key_nixos_anywhere
from clan_lib.ssh.remote import Remote
from clan_lib.vars.generate import run_generators

log = logging.getLogger(__name__)


BuildOn = Literal["auto", "local", "remote"]


Step = Literal[
    "generators",
    "upload-secrets",
    "nixos-anywhere",
    "formatting",
    "rebooting",
    "installing",
]


def notify_install_step(current: Step) -> None:
    message_queue.put(
        {
            "topic": current,
            "data": None,
            # MUST be set the to api function name, while technically you can set any origin, this is a bad idea.
            "origin": "run_machine_install",
        }
    )


@dataclass
class InstallOptions:
    machine: Machine
    kexec: str | None = None
    anywhere_priv_key: Path | None = None
    debug: bool = False
    no_reboot: bool = False
    phases: str | None = None
    build_on: BuildOn | None = None
    update_hardware_config: HardwareConfig = HardwareConfig.NONE
    persist_state: bool = True


@API.register
def run_machine_install(opts: InstallOptions, target_host: Remote) -> None:
    """Install a machine using nixos-anywhere.
    Args:
        opts: InstallOptions containing the machine to install, kexec option, debug mode,
            no-reboot option, phases, build-on option, hardware config update, password,
            identity file, and use_tor flag.
        target_host: Remote object representing the target host for installation.
    Raises:
        ClanError: If the machine is not found in the inventory or if there are issues with
            generating facts or variables.
    """
    machine = opts.machine

    machine.debug(f"installing {machine.name}")

    # Pre-cache vars attributes before generation to speed up installation
    config = nix_config()
    system = config["system"]
    machine_name = machine.name
    machine.flake.precache(
        [
            f"clanInternals.machines.{system}.{machine_name}.config.clan.core.vars.generators.*.validationHash",
            f"clanInternals.machines.{system}.{machine_name}.config.clan.core.vars.generators.*.{{share,dependencies,migrateFact,prompts}}",
            f"clanInternals.machines.{system}.{machine_name}.config.clan.core.vars.generators.*.files.*.{{secret,deploy,owner,group,mode,neededFor}}",
            f"clanInternals.machines.{system}.{machine_name}.config.clan.core.vars.settings.secretModule",
            f"clanInternals.machines.{system}.{machine_name}.config.clan.core.vars.settings.publicModule",
        ]
    )

    # Notify the UI about what we are doing
    notify_install_step("generators")
    generate_facts([machine])
    run_generators([machine])

    with (
        TemporaryDirectory(prefix="nixos-install-") as _base_directory,
    ):
        base_directory = Path(_base_directory).resolve()
        activation_secrets = base_directory / "activation_secrets"
        upload_dir = activation_secrets / machine.secrets_upload_directory.lstrip("/")
        upload_dir.mkdir(parents=True)

        # Notify the UI about what we are doing
        notify_install_step("upload-secrets")
        machine.secret_facts_store.upload(upload_dir)
        machine.secret_vars_store.populate_dir(
            machine.name, upload_dir, phases=["activation", "users", "services"]
        )

        partitioning_secrets = base_directory / "partitioning_secrets"
        partitioning_secrets.mkdir(parents=True)
        machine.secret_vars_store.populate_dir(
            machine.name, partitioning_secrets, phases=["partitioning"]
        )

        if target_host.password:
            os.environ["SSHPASS"] = target_host.password

        cmd = [
            "nixos-anywhere",
            "--flake",
            f"{machine.flake}#{machine.name}",
            "--extra-files",
            str(activation_secrets),
        ]

        for path in partitioning_secrets.rglob("*"):
            if path.is_file():
                cmd.extend(
                    [
                        "--disk-encryption-keys",
                        str(
                            "/run/partitioning-secrets"
                            / path.relative_to(partitioning_secrets)
                        ),
                        str(path),
                    ]
                )

        if opts.no_reboot:
            cmd.append("--no-reboot")

        if opts.phases:
            cmd += ["--phases", str(opts.phases)]

        if opts.update_hardware_config is not HardwareConfig.NONE:
            cmd.extend(
                [
                    "--generate-hardware-config",
                    str(opts.update_hardware_config.value),
                    str(opts.update_hardware_config.config_path(machine)),
                ]
            )

        if target_host.password:
            cmd += [
                "--env-password",
                "--ssh-option",
                "IdentitiesOnly=yes",
            ]

        # Always set a nixos-anywhere private key to prevent failures when running
        # 'clan install --phases kexec' followed by 'clan install --phases disko,install,reboot'.
        # The kexec phase requires an authorized key, and if not specified,
        # nixos-anywhere defaults to a key in a temporary directory.
        if opts.anywhere_priv_key is None:
            key_pair = create_secret_key_nixos_anywhere()
            opts.anywhere_priv_key = key_pair.private
        cmd += ["-i", str(opts.anywhere_priv_key)]

        # If we need a different private key for being able to kexec, we can specify it here.
        if target_host.private_key:
            cmd += ["--ssh-option", f"IdentityFile={target_host.private_key}"]

        if opts.build_on:
            cmd += ["--build-on", opts.build_on]

        if target_host.port:
            cmd += ["--ssh-port", str(target_host.port)]
        if opts.kexec:
            cmd += ["--kexec", opts.kexec]

        if opts.debug:
            cmd.append("--debug")

        # Add nix options to nixos-anywhere
        cmd.extend(opts.machine.flake.nix_options or [])

        cmd.append(target_host.target)
        if target_host.socks_port:
            # nix copy does not support socks5 proxy, use wrapper command
            wrapper = target_host.socks_wrapper
            wrapper_cmd = wrapper.cmd if wrapper else []
            wrapper_packages = wrapper.packages if wrapper else []
            cmd = nix_shell(
                [
                    "nixos-anywhere",
                    *wrapper_packages,
                ],
                [*wrapper_cmd, *cmd],
            )
        else:
            cmd = nix_shell(
                ["nixos-anywhere"],
                cmd,
            )

        notify_install_step("nixos-anywhere")
        run(
            [*cmd, "--phases", "kexec"],
            RunOpts(log=Log.BOTH, prefix=machine.name, needs_user_terminal=True),
        )
        notify_install_step("formatting")
        run(
            [*cmd, "--phases", "disko"],
            RunOpts(log=Log.BOTH, prefix=machine.name, needs_user_terminal=True),
        )
        notify_install_step("installing")
        run(
            [*cmd, "--phases", "install"],
            RunOpts(log=Log.BOTH, prefix=machine.name, needs_user_terminal=True),
        )
        notify_install_step("rebooting")
        run(
            [*cmd, "--phases", "reboot"],
            RunOpts(log=Log.BOTH, prefix=machine.name, needs_user_terminal=True),
        )

    if opts.persist_state:
        inventory_store = InventoryStore(machine.flake)
        inventory = inventory_store.read()

        set_value_by_path(
            inventory,
            f"machine.{machine.name}.installedAt",
            # Cut of the milliseconds
            int(time()),
        )
        inventory_store.write(
            inventory, f"Installed {machine.name} at {target_host.target}"
        )
