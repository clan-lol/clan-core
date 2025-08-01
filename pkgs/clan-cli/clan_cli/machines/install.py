import argparse
import logging
import sys
from pathlib import Path
from typing import get_args

from clan_lib.errors import ClanError
from clan_lib.flake import require_flake
from clan_lib.machines.install import BuildOn, InstallOptions, run_machine_install
from clan_lib.machines.machines import Machine
from clan_lib.ssh.host_key import HostKeyCheck
from clan_lib.ssh.remote import Remote

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
    complete_target_host,
)
from clan_cli.machines.hardware import HardwareConfig
from clan_cli.ssh.deploy_info import DeployInfo, find_reachable_host, ssh_command_parse

log = logging.getLogger(__name__)


def install_command(args: argparse.Namespace) -> None:
    try:
        flake = require_flake(args.flake)
        # Only if the caller did not specify a target_host via args.target_host
        # Find a suitable target_host that is reachable
        target_host_str = args.target_host
        deploy_info: DeployInfo | None = (
            ssh_command_parse(args) if target_host_str is None else None
        )

        use_tor = False
        if deploy_info:
            host = find_reachable_host(deploy_info)
            if host is None or host.socks_port:
                use_tor = True
                target_host_str = deploy_info.tor.target
            else:
                target_host_str = host.target

        if args.password:
            password = args.password
        elif deploy_info and deploy_info.addrs[0].password:
            password = deploy_info.addrs[0].password
        else:
            password = None

        machine = Machine(name=args.machine, flake=flake)
        host_key_check = args.host_key_check

        if target_host_str is not None:
            target_host = Remote.from_ssh_uri(
                machine_name=machine.name, address=target_host_str
            ).override(host_key_check=host_key_check)
        else:
            target_host = machine.target_host().override(host_key_check=host_key_check)

        if args.identity_file:
            target_host = target_host.override(private_key=args.identity_file)

        if machine._class_ == "darwin":
            msg = "Installing macOS machines is not yet supported"
            raise ClanError(msg)

        if not args.yes:
            while True:
                ask = (
                    input(f"Install {args.machine} to {target_host.target}? [y/N] ")
                    .strip()
                    .lower()
                )
                if ask == "y":
                    break
                if ask == "n" or ask == "":
                    return None
                print(f"Invalid input '{ask}'. Please enter 'y' for yes or 'n' for no.")

        if args.identity_file:
            target_host = target_host.override(private_key=args.identity_file)

        if password:
            target_host = target_host.override(password=password)

        if use_tor:
            target_host = target_host.override(
                socks_port=9050, socks_wrapper=["torify"]
            )

        return run_machine_install(
            InstallOptions(
                machine=machine,
                kexec=args.kexec,
                phases=args.phases,
                debug=args.debug,
                no_reboot=args.no_reboot,
                build_on=args.build_on if args.build_on is not None else None,
                update_hardware_config=HardwareConfig(args.update_hardware_config),
            ),
            target_host=target_host,
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
        choices=list(get_args(HostKeyCheck)),
        default="ask",
        help="Host key (.ssh/known_hosts) check mode.",
    )

    parser.add_argument(
        "--build-on",
        choices=list(get_args(BuildOn)),
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
