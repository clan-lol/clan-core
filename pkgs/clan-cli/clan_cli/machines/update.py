import argparse
import json
import os
import subprocess
from pathlib import Path

from ..cmd import run
from ..errors import ClanError
from ..machines.machines import Machine
from ..nix import nix_build, nix_command, nix_config
from ..secrets.generate import generate_secrets
from ..secrets.upload import upload_secrets
from ..ssh import Host, HostGroup, HostKeyCheck, parse_deployment_address


def deploy_nixos(hosts: HostGroup, clan_dir: Path) -> None:
    """
    Deploy to all hosts in parallel
    """

    def deploy(h: Host) -> None:
        target = f"{h.user or 'root'}@{h.host}"
        ssh_arg = f"-p {h.port}" if h.port else ""
        env = os.environ.copy()
        env["NIX_SSHOPTS"] = ssh_arg
        res = h.run_local(
            nix_command(["flake", "archive", "--to", f"ssh://{target}", "--json"]),
            check=True,
            stdout=subprocess.PIPE,
            extra_env=env,
        )
        data = json.loads(res.stdout)
        path = data["path"]

        if h.host_key_check != HostKeyCheck.STRICT:
            ssh_arg += " -o StrictHostKeyChecking=no"
        if h.host_key_check == HostKeyCheck.NONE:
            ssh_arg += " -o UserKnownHostsFile=/dev/null"

        ssh_arg += " -i " + h.key if h.key else ""

        flake_attr = h.meta.get("flake_attr", "")

        generate_secrets(h.meta["machine"])
        upload_secrets(h.meta["machine"])

        target_host = h.meta.get("target_host")
        if target_host:
            target_user = h.meta.get("target_user")
            if target_user:
                target_host = f"{target_user}@{target_host}"
        extra_args = h.meta.get("extra_args", [])
        cmd = [
            "nixos-rebuild",
            "switch",
            *extra_args,
            "--fast",
            "--option",
            "keep-going",
            "true",
            "--option",
            "accept-flake-config",
            "true",
            "--build-host",
            "",
            "--flake",
            f"{path}#{flake_attr}",
        ]
        if target_host:
            cmd.extend(["--target-host", target_host])
        ret = h.run(cmd, check=False)
        # re-retry switch if the first time fails
        if ret.returncode != 0:
            ret = h.run(cmd)

    hosts.run_function(deploy)


# function to speedup eval if we want to evauluate all machines
def get_all_machines(clan_dir: Path) -> HostGroup:
    config = nix_config()
    system = config["system"]
    machines_json = run(
        nix_build([f'{clan_dir}#clanInternals.all-machines-json."{system}"'])
    ).stdout

    machines = json.loads(Path(machines_json.rstrip()).read_text())

    hosts = []
    for name, machine_data in machines.items():
        # very hacky. would be better to do a MachinesGroup instead
        host = parse_deployment_address(
            name,
            machine_data.get("targetHost") or machine_data.get("deploymentAddress"),
            meta={
                "machine": Machine(
                    name=name, flake=clan_dir, deployment_info=machine_data
                )
            },
        )
        hosts.append(host)
    return HostGroup(hosts)


def get_selected_machines(machine_names: list[str], flake_dir: Path) -> HostGroup:
    hosts = []
    for name in machine_names:
        machine = Machine(name=name, flake=flake_dir)
        hosts.append(machine.host)
    return HostGroup(hosts)


# FIXME: we want some kind of inventory here.
def update(args: argparse.Namespace) -> None:
    if args.flake is None:
        raise ClanError("Could not find clan flake toplevel directory")
    if len(args.machines) == 1 and args.target_host is not None:
        machine = Machine(name=args.machines[0], flake=args.flake)
        machine.target_host = args.target_host
        host = parse_deployment_address(
            args.machines[0],
            args.target_host,
            meta={"machine": machine},
        )
        machines = HostGroup([host])

    elif args.target_host is not None:
        print("target host can only be specified for a single machine")
        exit(1)
    else:
        if len(args.machines) == 0:
            machines = get_all_machines(args.flake)
        else:
            machines = get_selected_machines(args.machines, args.flake)

    deploy_nixos(machines, args.flake)


def register_update_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machines",
        type=str,
        help="machine to update. if empty, update all machines",
        nargs="*",
        default=[],
    )
    parser.add_argument(
        "--target-host",
        type=str,
        help="address of the machine to update, in the format of user@host:1234",
    )
    parser.set_defaults(func=update)
