import argparse
import json
import os
import subprocess
from typing import Optional

from ..dirs import get_clan_flake_toplevel
from ..nix import nix_eval
from ..secrets.generate import generate_secrets
from ..secrets.upload import upload_secrets
from ..ssh import Host, HostGroup, HostKeyCheck


def deploy_nixos(hosts: HostGroup) -> None:
    """
    Deploy to all hosts in parallel
    """

    def deploy(h: Host) -> None:
        target = f"{h.user or 'root'}@{h.host}"
        ssh_arg = f"-p {h.port}" if h.port else ""
        env = os.environ.copy()
        env["NIX_SSHOPTS"] = ssh_arg
        res = h.run_local(
            ["nix", "flake", "archive", "--to", f"ssh://{target}", "--json"],
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

        generate_secrets(h.host)
        upload_secrets(h.host)

        flake_attr = h.meta.get("flake_attr", "")
        if flake_attr:
            flake_attr = "#" + flake_attr
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
                f"{path}{flake_attr}",
            ]
        )
        if target_host:
            cmd.extend(["--target-host", target_host])
        ret = h.run(cmd, check=False)
        # re-retry switch if the first time fails
        if ret.returncode != 0:
            ret = h.run(cmd)

    hosts.run_function(deploy)


# FIXME: we want some kind of inventory here.
def update(args: argparse.Namespace) -> None:
    clan_dir = get_clan_flake_toplevel().as_posix()
    host = json.loads(
        subprocess.run(
            nix_eval(
                [
                    f'{clan_dir}#nixosConfigurations."{args.machine}".config.clan.networking.deploymentAddress'
                ]
            ),
            stdout=subprocess.PIPE,
            check=True,
            text=True,
        ).stdout
    )
    parts = host.split("@")
    user: Optional[str] = None
    if len(parts) > 1:
        user = parts[0]
        hostname = parts[1]
    else:
        hostname = parts[0]
    maybe_port = hostname.split(":")
    port = None
    if len(maybe_port) > 1:
        hostname = maybe_port[0]
        port = int(maybe_port[1])
    print(f"deploying {host}")
    deploy_nixos(HostGroup([Host(host=hostname, port=port, user=user)]))


def register_update_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--target-host", type=str, default="root")
    parser.add_argument("machine", type=str)
    parser.set_defaults(func=update)
