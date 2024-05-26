import argparse
import importlib
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from ..cmd import Log, run
from ..facts.generate import generate_facts
from ..machines.machines import Machine
from ..nix import nix_shell
from ..ssh.cli import is_ipv6, is_reachable, qrcode_scan

log = logging.getLogger(__name__)


class ClanError(Exception):
    pass


def install_nixos(
    machine: Machine,
    kexec: str | None = None,
    debug: bool = False,
    password: str | None = None,
    no_reboot: bool = False,
) -> None:
    secret_facts_module = importlib.import_module(machine.secret_facts_module)
    log.info(f"installing {machine.name}")
    secret_facts_store = secret_facts_module.SecretStore(machine=machine)

    h = machine.target_host
    target_host = f"{h.user or 'root'}@{h.host}"
    log.info(f"target host: {target_host}")

    generate_facts([machine], None)

    with TemporaryDirectory() as tmpdir_:
        tmpdir = Path(tmpdir_)
        upload_dir_ = machine.secrets_upload_directory

        if upload_dir_.startswith("/"):
            upload_dir_ = upload_dir_[1:]
        upload_dir = tmpdir / upload_dir_
        upload_dir.mkdir(parents=True)
        secret_facts_store.upload(upload_dir)

        if password:
            os.environ["SSHPASS"] = password

        cmd = [
            "nixos-anywhere",
            "--flake",
            f"{machine.flake}#{machine.name}",
            "--extra-files",
            str(tmpdir),
        ]

        if no_reboot:
            cmd.append("--no-reboot")

        if password:
            cmd += [
                "--env-password",
                "--ssh-option",
                "IdentitiesOnly=yes",
            ]

        if machine.target_host.port:
            cmd += ["--ssh-port", str(machine.target_host.port)]
        if kexec:
            cmd += ["--kexec", kexec]
        if debug:
            cmd.append("--debug")
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
    confirm: bool
    debug: bool
    no_reboot: bool
    json_ssh_deploy: dict[str, str] | None


def install_command(args: argparse.Namespace) -> None:
    json_ssh_deploy = None
    if args.json:
        json_file = Path(args.json)
        if json_file.is_file():
            json_ssh_deploy = json.loads(json_file.read_text())
        else:
            json_ssh_deploy = json.loads(args.json)
    elif args.png:
        json_ssh_deploy = json.loads(qrcode_scan(args.png))

    if not json_ssh_deploy and not args.target_host:
        raise ClanError("No target host provided, please provide a target host.")

    if json_ssh_deploy:
        target_host = f"root@{find_reachable_host_from_deploy_json(json_ssh_deploy)}"
        password = json_ssh_deploy["pass"]
    else:
        target_host = args.target_host
        password = None

    opts = InstallOptions(
        flake=args.flake,
        machine=args.machine,
        target_host=target_host,
        kexec=args.kexec,
        confirm=not args.yes,
        debug=args.debug,
        no_reboot=args.no_reboot,
        json_ssh_deploy=json_ssh_deploy,
    )
    machine = Machine(opts.machine, flake=opts.flake)
    machine.target_host_address = opts.target_host

    if opts.confirm:
        ask = input(f"Install {machine.name} to {opts.target_host}? [y/N] ")
        if ask != "y":
            return

    install_nixos(
        machine,
        kexec=opts.kexec,
        debug=opts.debug,
        password=password,
        no_reboot=opts.no_reboot,
    )


def find_reachable_host_from_deploy_json(deploy_json: dict[str, str]) -> str:
    host = None
    for addr in deploy_json["addrs"]:
        if is_reachable(addr):
            if is_ipv6(addr):
                host = f"[{addr}]"
            else:
                host = addr
            break
    if not host:
        raise ClanError(
            f"""
            Could not reach any of the host addresses provided in the json string.
            Please doublecheck if they are reachable from your machine.
            Try `ping [ADDR]` with one of the addresses: {deploy_json['addrs']}
            """
        )
    return host


def register_install_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--kexec",
        type=str,
        help="use another kexec tarball to bootstrap NixOS",
    )
    parser.add_argument(
        "--no-reboot",
        action="store_true",
        help="do not reboot after installation",
        default=False,
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="do not ask for confirmation",
        default=False,
    )
    parser.add_argument(
        "machine",
        type=str,
        help="machine to install",
    )
    parser.add_argument(
        "target_host",
        type=str,
        nargs="?",
        help="ssh address to install to in the form of user@host:2222",
    )
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-j",
        "--json",
        help="specify the json file for ssh data (generated by starting the clan installer)",
    )
    group.add_argument(
        "-P",
        "--png",
        help="specify the json file for ssh data as the qrcode image (generated by starting the clan installer)",
    )
    parser.set_defaults(func=install_command)
