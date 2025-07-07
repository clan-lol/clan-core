import logging
import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory

from clan_cli.facts.generate import generate_facts
from clan_cli.machines.hardware import HardwareConfig
from clan_cli.vars.generate import generate_vars

from clan_lib.api import API
from clan_lib.cmd import Log, RunOpts, run
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_shell
from clan_lib.ssh.remote import Remote

log = logging.getLogger(__name__)


class BuildOn(Enum):
    AUTO = "auto"
    LOCAL = "local"
    REMOTE = "remote"


@dataclass
class InstallOptions:
    machine: Machine
    kexec: str | None = None
    debug: bool = False
    no_reboot: bool = False
    phases: str | None = None
    build_on: BuildOn | None = None
    update_hardware_config: HardwareConfig = HardwareConfig.NONE
    password: str | None = None
    identity_file: Path | None = None
    use_tor: bool = False


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

    generate_facts([machine])
    generate_vars([machine])

    with (
        TemporaryDirectory(prefix="nixos-install-") as _base_directory,
    ):
        base_directory = Path(_base_directory).resolve()
        activation_secrets = base_directory / "activation_secrets"
        upload_dir = activation_secrets / machine.secrets_upload_directory.lstrip("/")
        upload_dir.mkdir(parents=True)
        machine.secret_facts_store.upload(upload_dir)
        machine.secret_vars_store.populate_dir(
            upload_dir, phases=["activation", "users", "services"]
        )

        partitioning_secrets = base_directory / "partitioning_secrets"
        partitioning_secrets.mkdir(parents=True)
        machine.secret_vars_store.populate_dir(
            partitioning_secrets, phases=["partitioning"]
        )

        if opts.password:
            os.environ["SSHPASS"] = opts.password

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

        if opts.password:
            cmd += [
                "--env-password",
                "--ssh-option",
                "IdentitiesOnly=yes",
            ]

        if opts.identity_file:
            cmd += ["-i", str(opts.identity_file)]

        if opts.build_on:
            cmd += ["--build-on", opts.build_on.value]

        if target_host.port:
            cmd += ["--ssh-port", str(target_host.port)]
        if opts.kexec:
            cmd += ["--kexec", opts.kexec]

        if opts.debug:
            cmd.append("--debug")

        # Add nix options to nixos-anywhere
        cmd.extend(opts.machine.flake.nix_options or [])

        cmd.append(target_host.target)
        if opts.use_tor:
            # nix copy does not support tor socks proxy
            # cmd.append("--ssh-option")
            # cmd.append("ProxyCommand=nc -x 127.0.0.1:9050 -X 5 %h %p")
            cmd = nix_shell(
                [
                    "nixos-anywhere",
                    "tor",
                ],
                ["torify", *cmd],
            )
        else:
            cmd = nix_shell(
                ["nixos-anywhere"],
                cmd,
            )
        run(cmd, RunOpts(log=Log.BOTH, prefix=machine.name, needs_user_terminal=True))
