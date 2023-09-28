import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from ..dirs import get_clan_flake_toplevel
from ..nix import nix_build, nix_command, nix_config
from ..secrets.generate import run_generate_secrets
from ..secrets.upload import run_upload_secrets
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

        if generate_secrets_script := h.meta.get("generate_secrets"):
            run_generate_secrets(generate_secrets_script, clan_dir)

        if upload_secrets_script := h.meta.get("upload_secrets"):
            run_upload_secrets(upload_secrets_script, clan_dir)

        target_host = h.meta.get("target_host")
        if target_host:
            target_user = h.meta.get("target_user")
            if target_user:
                target_host = f"{target_user}@{target_host}"
        extra_args = h.meta.get("extra_args", [])
        cmd = (
            ["nixos-rebuild", "switch"]
            + extra_args
            + [
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
        )
        if target_host:
            cmd.extend(["--target-host", target_host])
        ret = h.run(cmd, check=False)
        # re-retry switch if the first time fails
        if ret.returncode != 0:
            ret = h.run(cmd)

    hosts.run_function(deploy)


def build_json(targets: list[str]) -> list[dict[str, Any]]:
    outpaths = subprocess.run(
        nix_build(targets),
        stdout=subprocess.PIPE,
        check=True,
        text=True,
    ).stdout
    parsed = []
    for outpath in outpaths.splitlines():
        parsed.append(json.loads(Path(outpath).read_text()))
    return parsed


def get_all_machines(clan_dir: Path) -> HostGroup:
    config = nix_config()
    system = config["system"]
    what = f'{clan_dir}#clanInternals.machines-json."{system}"'
    machines = build_json([what])[0]

    hosts = []
    for name, machine in machines.items():
        host = parse_deployment_address(
            name, machine["deploymentAddress"], meta=machine
        )
        hosts.append(host)
    return HostGroup(hosts)


def get_selected_machines(machine_names: list[str], clan_dir: Path) -> HostGroup:
    config = nix_config()
    system = config["system"]
    what = []
    for name in machine_names:
        what.append(f'{clan_dir}#clanInternals.machines."{system}"."{name}".json')
    machines = build_json(what)
    hosts = []
    for i, machine in enumerate(machines):
        host = parse_deployment_address(machine_names[i], machine["deploymentAddress"])
        hosts.append(host)
    return HostGroup(hosts)


# FIXME: we want some kind of inventory here.
def update(args: argparse.Namespace) -> None:
    clan_dir = get_clan_flake_toplevel()
    if len(args.machines) == 0:
        machines = get_all_machines(clan_dir)
    else:
        machines = get_selected_machines(args.machines, clan_dir)

    deploy_nixos(machines, clan_dir)


def register_update_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "machines",
        type=str,
        help="machine to update. if empty, update all machines",
        nargs="*",
        default=[],
    )
    parser.set_defaults(func=update)
