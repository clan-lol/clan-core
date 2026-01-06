import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory
from time import time
from typing import Literal

from clan_cli.machines.hardware import HardwareConfig

from clan_lib.api import API, message_queue
from clan_lib.cmd import Log, RunOpts, run
from clan_lib.git import commit_file
from clan_lib.machines.machines import Machine
from clan_lib.machines.nixos_anywhere import (
    add_debug,
    add_kexec,
    add_nix_options,
    add_nixos_anywhere_key,
    add_password_options,
    add_ssh_port,
    add_target,
    add_target_private_key,
    add_test_store_workaround,
    setup_environ,
    wrap_nix_shell,
)
from clan_lib.nix import nix_config
from clan_lib.nix_selectors import (
    vars_generators_files,
    vars_generators_metadata,
    vars_settings_public_module,
    vars_settings_secret_module,
)
from clan_lib.persist.inventory_store import InventoryStore
from clan_lib.persist.path_utils import set_value_by_path
from clan_lib.ssh.remote import Remote
from clan_lib.vars.generate import run_generators

log = logging.getLogger(__name__)


BuildOn = Literal["auto", "local", "remote"]


class Step(str, Enum):
    GENERATORS = "generators"
    UPLOAD_SECRETS = "upload-secrets"
    NIXOS_ANYWHERE = "nixos-anywhere"
    FORMATTING = "formatting"
    REBOOTING = "rebooting"
    INSTALLING = "installing"


def notify_install_step(current: Step) -> None:
    print(f"NOTIFY STEP: {current}")
    message_queue.put(
        {
            "topic": current,
            "data": None,
            # MUST be set the to api function name, while technically you can set any origin, this is a bad idea.
            "origin": "run_machine_install",
        },
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
            generating vars.

    """
    machine = opts.machine

    machine.debug(f"installing {machine.name}")

    # Pre-cache vars attributes before generation to speed up installation
    config = nix_config()
    system = config["system"]
    machine_name = machine.name
    machine.flake.precache(
        [
            vars_generators_metadata(system, [machine_name]),
            vars_generators_files(system, [machine_name]),
            vars_settings_secret_module(system, [machine_name]),
            vars_settings_public_module(system, [machine_name]),
        ],
    )

    # Notify the UI about what we are doing
    notify_install_step(Step.GENERATORS)
    run_generators([machine], generators=None, full_closure=False)

    with (
        TemporaryDirectory(prefix="nixos-install-") as _base_directory,
    ):
        # /tmp-234/
        base_directory = Path(_base_directory).resolve()

        # /tmp-234/activation_secrets/
        activation_secrets = base_directory / "activation_secrets"

        # Notify the UI about what we are doing
        notify_install_step(Step.UPLOAD_SECRETS)

        # Get upload directory, falling back if backend doesn't support remote install
        secrets_target_dir = machine.secret_vars_store.get_upload_directory(
            machine.name
        )
        # /tmp-234/activation_secrets/var/lib/sops-nix
        upload_dir = activation_secrets / secrets_target_dir.lstrip("/")

        upload_dir.mkdir(parents=True)
        # /tmp-234/activation_secrets/var/lib/sops-nix/{activation,key.txt}
        machine.secret_vars_store.populate_dir(
            machine.name,
            upload_dir,
            phases=["activation", "users", "services"],
        )

        # /tmp-234/activation_secrets/var/lib/sops-nix/{gen_1/file_1,gen_2/file_2}
        partitioning_secrets = base_directory / "partitioning_secrets"
        partitioning_secrets.mkdir(parents=True)
        machine.secret_vars_store.populate_dir(
            machine.name,
            partitioning_secrets,
            phases=["partitioning"],
        )

        cmd = [
            "nixos-anywhere",
            "--flake",
            f"{machine.flake}#{machine.name}",
            # Mark the
            "--extra-files",
            str(activation_secrets),
        ]

        # for every file in the partitioning_secrets file-tree
        # Append one command "--disk-encryption-keys file_x"
        for path in partitioning_secrets.rglob("*"):
            if path.is_file():
                cmd.extend(
                    [
                        "--disk-encryption-keys",
                        str(
                            "/run/partitioning-secrets"
                            / path.relative_to(partitioning_secrets),
                        ),
                        str(path),
                    ],
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
                ],
            )

        environ = setup_environ(target_host)
        cmd = add_password_options(cmd, target_host)

        # Always set a nixos-anywhere private key to prevent failures when running
        # 'clan install --phases kexec' followed by 'clan install --phases disko,install,reboot'.
        # The kexec phase requires an authorized key, and if not specified,
        # nixos-anywhere defaults to a key in a temporary directory.
        if opts.anywhere_priv_key is None:
            cmd, key_pair = add_nixos_anywhere_key(cmd)
            opts.anywhere_priv_key = key_pair.private
        else:
            cmd, _ = add_nixos_anywhere_key(cmd, opts.anywhere_priv_key)

        # If we need a different private key for being able to kexec, we can specify it here.
        cmd = add_target_private_key(cmd, target_host)

        if opts.build_on:
            cmd += ["--build-on", opts.build_on]

        cmd = add_ssh_port(cmd, target_host)
        cmd = add_kexec(cmd, opts.kexec)
        cmd = add_debug(cmd, opts.debug)
        cmd = add_test_store_workaround(cmd, environ)
        cmd = add_nix_options(cmd, machine)
        cmd = add_target(cmd, target_host)
        cmd = wrap_nix_shell(cmd, target_host)

        install_steps = {
            "kexec": Step.NIXOS_ANYWHERE,
            "disko": Step.FORMATTING,
            "install": Step.INSTALLING,
            "reboot": Step.REBOOTING,
        }

        def run_phase(phase: str) -> None:
            notification = install_steps.get(phase, Step.NIXOS_ANYWHERE)
            notify_install_step(notification)
            # breakpoint()
            run(
                [*cmd, "--phases", phase],
                RunOpts(
                    log=Log.BOTH,
                    prefix=machine.name,
                    needs_user_terminal=True,
                    env=environ,
                ),
            )

        if opts.phases:
            phases = [phase.strip() for phase in opts.phases.split(",")]
            for phase in phases:
                run_phase(phase)
        else:
            for phase in ["kexec", "disko", "install", "reboot"]:
                run_phase(phase)

    if opts.update_hardware_config is not HardwareConfig.NONE:
        hw_file = opts.update_hardware_config.config_path(machine)
        if hw_file.exists():
            commit_file(
                hw_file,
                opts.machine.flake.path,
                f"machines/{opts.machine.name}/{hw_file.name}: update hardware configuration",
            )

    if opts.persist_state:
        inventory_store = InventoryStore(machine.flake)
        inventory = inventory_store.read()

        set_value_by_path(
            inventory,
            f"machines.{machine.name}.installedAt",
            # Cut of the milliseconds
            int(time()),
        )
        inventory_store.write(
            inventory,
            f"Installed {machine.name}",
        )
