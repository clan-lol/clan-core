import argparse
import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clan_lib.cmd import run
from clan_lib.errors import ClanError
from clan_lib.nix import nix_shell
from clan_lib.ssh.remote import HostKeyCheck, Remote

from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
)
from clan_cli.ssh.tor import TorTarget, spawn_tor, ssh_tor_reachable

log = logging.getLogger(__name__)


@dataclass
class DeployInfo:
    addrs: list[Remote]

    @property
    def tor(self) -> Remote:
        """Return a list of Remote objects that are configured for Tor."""
        addrs = [addr for addr in self.addrs if addr.tor_socks]

        if not addrs:
            msg = "No tor address provided, please provide a tor address."
            raise ClanError(msg)

        if len(addrs) > 1:
            msg = "Multiple tor addresses provided, expected only one."
            raise ClanError(msg)
        return addrs[0]

    @staticmethod
    def from_hostnames(
        hostname: list[str], host_key_check: HostKeyCheck
    ) -> "DeployInfo":
        remotes = []
        for host in hostname:
            if not host:
                msg = "Hostname cannot be empty."
                raise ClanError(msg)
            remote = Remote.from_ssh_uri(
                machine_name="clan-installer", address=host
            ).override(host_key_check=host_key_check)
            remotes.append(remote)
        return DeployInfo(addrs=remotes)

    @staticmethod
    def from_json(data: dict[str, Any], host_key_check: HostKeyCheck) -> "DeployInfo":
        addrs = []
        password = data.get("pass")

        for addr in data.get("addrs", []):
            if isinstance(addr, str):
                remote = Remote.from_ssh_uri(
                    machine_name="clan-installer",
                    address=addr,
                ).override(host_key_check=host_key_check, password=password)
                addrs.append(remote)
            else:
                msg = f"Invalid address format: {addr}"
                raise ClanError(msg)
        if tor_addr := data.get("tor"):
            remote = Remote.from_ssh_uri(
                machine_name="clan-installer",
                address=tor_addr,
            ).override(host_key_check=host_key_check, tor_socks=True, password=password)
            addrs.append(remote)

        return DeployInfo(addrs=addrs)

    @staticmethod
    def from_qr_code(picture_file: Path, host_key_check: HostKeyCheck) -> "DeployInfo":
        cmd = nix_shell(
            ["zbar"],
            [
                "zbarimg",
                "--quiet",
                "--raw",
                str(picture_file),
            ],
        )
        res = run(cmd)
        data = res.stdout.strip()
        return DeployInfo.from_json(json.loads(data), host_key_check=host_key_check)


def find_reachable_host(deploy_info: DeployInfo) -> Remote | None:
    # If we only have one address, we have no choice but to use it.
    if len(deploy_info.addrs) == 1:
        return deploy_info.addrs[0]

    for addr in deploy_info.addrs:
        if addr.is_ssh_reachable():
            return addr
    return None


def ssh_shell_from_deploy(deploy_info: DeployInfo) -> None:
    if host := find_reachable_host(deploy_info):
        host.interactive_ssh()
        return

    log.info("Could not reach host via clearnet 'addrs'")
    log.info(f"Trying to reach host via tor '{deploy_info}'")

    tor_addrs = [addr for addr in deploy_info.addrs if addr.tor_socks]
    if not tor_addrs:
        msg = "No tor address provided, please provide a tor address."
        raise ClanError(msg)

    with spawn_tor():
        for tor_addr in tor_addrs:
            log.info(f"Trying to reach host via tor address: {tor_addr}")
            if ssh_tor_reachable(
                TorTarget(
                    onion=tor_addr.address, port=tor_addr.port if tor_addr.port else 22
                )
            ):
                log.info(
                    "Host reachable via tor address, starting interactive ssh session."
                )
                tor_addr.interactive_ssh()
                return

        log.error("Could not reach host via tor address.")


def ssh_command_parse(args: argparse.Namespace) -> DeployInfo | None:
    host_key_check = args.host_key_check
    if args.json:
        json_file = Path(args.json)
        if json_file.is_file():
            data = json.loads(json_file.read_text())
            return DeployInfo.from_json(data, host_key_check)
        data = json.loads(args.json)
        return DeployInfo.from_json(data, host_key_check)
    if args.png:
        return DeployInfo.from_qr_code(Path(args.png), host_key_check)

    if hasattr(args, "machines"):
        return DeployInfo.from_hostnames(args.machines, host_key_check)
    return None


def ssh_command(args: argparse.Namespace) -> None:
    deploy_info = ssh_command_parse(args)
    if not deploy_info:
        msg = "No MACHINE, --json or --png data provided"
        raise ClanError(msg)

    ssh_shell_from_deploy(deploy_info)


def register_parser(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group(required=True)
    machines_parser = group.add_argument(
        "machines",
        type=str,
        nargs="*",
        default=[],
        metavar="MACHINE",
        help="Machine to ssh into.",
    )
    add_dynamic_completer(machines_parser, complete_machines)

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
    parser.add_argument(
        "--host-key-check",
        choices=["strict", "ask", "tofu", "none"],
        default="tofu",
        help="Host key (.ssh/known_hosts) check mode.",
    )
    parser.set_defaults(func=ssh_command)
