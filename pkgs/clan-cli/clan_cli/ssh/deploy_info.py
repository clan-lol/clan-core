import argparse
import json
import logging
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from clan_lib.cmd import run
from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
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

    def overwrite_remotes(
        self,
        host_key_check: HostKeyCheck | None = None,
        private_key: Path | None = None,
        ssh_options: dict[str, str] | None = None,
    ) -> "DeployInfo":
        """Return a new DeployInfo with all Remotes overridden with the given host_key_check."""
        return DeployInfo(
            addrs=[
                addr.override(
                    host_key_check=host_key_check,
                    private_key=private_key,
                    ssh_options=ssh_options,
                )
                for addr in self.addrs
            ]
        )

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
        if addr.check_machine_ssh_reachable():
            return addr
    return None


def ssh_shell_from_deploy(
    deploy_info: DeployInfo, command: list[str] | None = None
) -> None:
    if command and len(command) == 1 and command[0].count(" ") > 0:
        msg = (
            textwrap.dedent("""
            It looks like you quoted the remote command.
            The first argument should be the command to run, not a quoted string.
        """)
            .lstrip("\n")
            .rstrip("\n")
        )
        raise ClanError(msg)

    if host := find_reachable_host(deploy_info):
        host.interactive_ssh(command)
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
                tor_addr.interactive_ssh(command)
                return

        log.error("Could not reach host via tor address.")


def ssh_command_parse(args: argparse.Namespace) -> DeployInfo | None:
    host_key_check = args.host_key_check
    deploy = None
    if args.json:
        json_file = Path(args.json)
        if json_file.is_file():
            data = json.loads(json_file.read_text())
            return DeployInfo.from_json(data, host_key_check)
        data = json.loads(args.json)
        deploy = DeployInfo.from_json(data, host_key_check)
    if args.png:
        deploy = DeployInfo.from_qr_code(Path(args.png), host_key_check)

    if hasattr(args, "machine") and args.machine:
        machine = Machine(args.machine, args.flake)
        target = machine.target_host().override(
            command_prefix=machine.name, host_key_check=host_key_check
        )
        deploy = DeployInfo(addrs=[target])

    if deploy is None:
        return None

    ssh_options = {}
    for name, value in args.ssh_option or []:
        ssh_options[name] = value
    deploy = deploy.overwrite_remotes(ssh_options=ssh_options)
    return deploy


def ssh_command(args: argparse.Namespace) -> None:
    deploy_info = ssh_command_parse(args)
    if not deploy_info:
        msg = "No MACHINE, --json or --png data provided"
        raise ClanError(msg)
    ssh_shell_from_deploy(deploy_info, args.remote_command)


def register_parser(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "machine",
        type=str,
        nargs="?",
        metavar="MACHINE",
        help="Machine to ssh into (uses clan.core.networking.targetHost from configuration).",
    )

    group.add_argument(
        "-j",
        "--json",
        type=str,
        help=(
            "Deployment information as a JSON string or path to a JSON file "
            "(generated by starting the clan installer)."
        ),
    )
    group.add_argument(
        "-P",
        "--png",
        type=str,
        help="Deployment information as a QR code image file (generated by starting the clan installer).",
    )

    parser.add_argument(
        "--host-key-check",
        choices=["strict", "ask", "tofu", "none"],
        default="tofu",
        help="Host key (.ssh/known_hosts) check mode.",
    )

    parser.add_argument(
        "--ssh-option",
        help="SSH option to set (can be specified multiple times)",
        nargs=2,
        metavar=("name", "value"),
        action="append",
        default=[],
    )

    parser.add_argument(
        "-c",
        "--remote-command",
        type=str,
        metavar="COMMAND",
        nargs=argparse.REMAINDER,
        help="Command to execute on the remote host, needs to be the LAST argument as it takes all remaining arguments.",
    )

    add_dynamic_completer(
        parser._actions[1],  # noqa: SLF001
        complete_machines,
    )  # assumes 'machine' is the first positional

    parser.set_defaults(func=ssh_command)
