import argparse
import logging
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from tempfile import TemporaryDirectory

from clan_cli.api import API
from clan_cli.cmd import Log, RunOpts, run
from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_target_host,
)
from clan_cli.errors import ClanError
from clan_cli.facts.generate import generate_facts
from clan_cli.machines.hardware import HardwareConfig
from clan_cli.machines.machines import Machine
from clan_cli.nix import nix_shell
from clan_cli.ssh.deploy_info import DeployInfo, find_reachable_host, ssh_command_parse
from clan_cli.ssh.host_key import HostKeyCheck
from clan_cli.vars.generate import generate_vars

log = logging.getLogger(__name__)


class BuildOn(Enum):
    AUTO = "auto"
    LOCAL = "local"
    REMOTE = "remote"


@dataclass
class InstallOptions:
    machine: Machine
    target_host: str
    kexec: str | None = None
    debug: bool = False
    no_reboot: bool = False
    phases: str | None = None
    build_on: BuildOn | None = None
    nix_options: list[str] = field(default_factory=list)
    update_hardware_config: HardwareConfig = HardwareConfig.NONE
    password: str | None = None
    identity_file: Path | None = None
    use_tor: bool = False


@API.register
def install_machine(opts: InstallOptions) -> None:
    machine = opts.machine
    machine.override_target_host = opts.target_host

    machine.info(f"installing {machine.name}")

    h = machine.target_host
    machine.info(f"target host: {h.target}")

    generate_facts([machine])
    generate_vars([machine])

    with TemporaryDirectory(prefix="nixos-install-") as _base_directory:
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
                    str(
                        opts.update_hardware_config.config_path(
                            machine.flake.path, machine.name
                        )
                    ),
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

        if h.port:
            cmd += ["--ssh-port", str(h.port)]
        if opts.kexec:
            cmd += ["--kexec", opts.kexec]

        if opts.debug:
            cmd.append("--debug")
        cmd.append(h.target)
        if opts.use_tor:
            # nix copy does not support tor socks proxy
            # cmd.append("--ssh-option")
            # cmd.append("ProxyCommand=nc -x 127.0.0.1:9050 -X 5 %h %p")
            run(
                nix_shell(
                    [
                        "nixpkgs#nixos-anywhere",
                        "nixpkgs#tor",
                    ],
                    ["torify", *cmd],
                ),
                RunOpts(log=Log.BOTH, prefix=machine.name, needs_user_terminal=True),
            )
        else:
            run(
                nix_shell(
                    ["nixpkgs#nixos-anywhere"],
                    cmd,
                ),
                RunOpts(log=Log.BOTH, prefix=machine.name, needs_user_terminal=True),
            )


def install_command(args: argparse.Namespace) -> None:
    host_key_check = HostKeyCheck.from_str(args.host_key_check)
    try:
        machine = Machine(name=args.machine, flake=args.flake, nix_options=args.option)
        use_tor = False

        if args.flake is None:
            #
            msg = "Could not find clan flake toplevel directory"
            raise ClanError(msg)

        deploy_info: DeployInfo | None = ssh_command_parse(args)

        if args.target_host:
            target_host = args.target_host
        elif deploy_info:
            host = find_reachable_host(deploy_info, host_key_check)
            if host is None:
                use_tor = True
                target_host = f"root@{deploy_info.tor}"
            else:
                target_host = host.target
            password = deploy_info.pwd
        else:
            target_host = machine.target_host.target

        if args.password:
            password = args.password
        elif deploy_info and deploy_info.pwd:
            password = deploy_info.pwd
        else:
            password = None

        if not target_host:
            msg = "No target host provided, please provide a target host."
            raise ClanError(msg)

        if not args.yes:
            ask = input(f"Install {args.machine} to {target_host}? [y/N] ")
            if ask != "y":
                return None

        return install_machine(
            InstallOptions(
                machine=machine,
                target_host=target_host,
                kexec=args.kexec,
                phases=args.phases,
                debug=args.debug,
                no_reboot=args.no_reboot,
                nix_options=args.option,
                build_on=BuildOn(args.build_on) if args.build_on is not None else None,
                update_hardware_config=HardwareConfig(args.update_hardware_config),
                password=password,
                identity_file=args.identity_file,
                use_tor=use_tor,
            ),
        )
    except KeyboardInterrupt:
        log.warning("Interrupted by user")
        sys.exit(1)


def register_install_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--kexec",
        type=str,
        help="use another kexec tarball to bootstrap NixOS",
    )
    parser.add_argument(
        "--no-reboot",
        action="store_true",
        help="do not reboot after installation (deprecated)",
        default=False,
    )
    parser.add_argument(
        "--host-key-check",
        choices=["strict", "ask", "tofu", "none"],
        default="ask",
        help="Host key (.ssh/known_hosts) check mode.",
    )
    parser.add_argument(
        "--build-on",
        choices=[x.value for x in BuildOn],
        default=None,
        help="where to build the NixOS configuration",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="do not ask for confirmation",
        default=False,
    )
    parser.add_argument(
        "--update-hardware-config",
        type=str,
        default="none",
        help="update the hardware configuration",
        choices=[x.value for x in HardwareConfig],
    )

    parser.add_argument(
        "--phases",
        type=str,
        help="comma separated list of phases to run. Default is: kexec,disko,install,reboot",
    )

    machines_parser = parser.add_argument(
        "machine",
        type=str,
        help="machine to install",
    )
    add_dynamic_completer(machines_parser, complete_machines)

    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-j",
        "--json",
        help="specify the json file for ssh data (generated by starting the clan installer)",
    )
    target_host_parser = group.add_argument(
        "--target-host",
        help="ssh address to install to in the form of user@host:2222",
    )
    add_dynamic_completer(target_host_parser, complete_target_host)
    authentication_group = parser.add_mutually_exclusive_group()
    authentication_group.add_argument(
        "--password",
        help="specify the password for the ssh connection (generated by starting the clan installer)",
    )
    authentication_group.add_argument(
        "-i",
        dest="identity_file",
        type=Path,
        help="specify which SSH private key file to use",
    )
    group.add_argument(
        "-P",
        "--png",
        help="specify the json file for ssh data as the qrcode image (generated by starting the clan installer)",
    )

    parser.set_defaults(func=install_command)
