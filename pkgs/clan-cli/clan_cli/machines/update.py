import argparse
import json
import os
import subprocess

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
            extra_env=env
        )
        data = json.loads(res.stdout)
        path = data["path"]

        if h.host_key_check != HostKeyCheck.STRICT:
            ssh_arg += " -o StrictHostKeyChecking=no"
        if h.host_key_check == HostKeyCheck.NONE:
            ssh_arg += " -o UserKnownHostsFile=/dev/null"

        ssh_arg += " -i " + h.key if h.key else ""

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
    meta = {}
    if args.flake_uri:
        meta["flake_uri"] = args.flake_uri
    if args.flake_attr:
        meta["flake_attr"] = args.flake_attr
    deploy_nixos(HostGroup([Host(args.host, user=args.user, meta=meta)]))


def register_update_parser(parser: argparse.ArgumentParser) -> None:
    # TODO pass all args we don't parse into ssh_args, currently it fails if arg starts with -
    parser.add_argument("--flake-uri", type=str, default=".#", help="nix flake uri")
    parser.add_argument(
        "--flake-attr", type=str, help="nixos configuration in the flake"
    )
    parser.add_argument("--user", type=str, default="root")
    parser.add_argument("host", type=str)
    parser.set_defaults(func=update)
