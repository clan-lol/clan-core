import argparse
import json
import subprocess

from .ssh import Host, HostGroup, HostKeyCheck


def deploy_nixos(hosts: HostGroup) -> None:
    """
    Deploy to all hosts in parallel
    """

    flake_store_paths = {}
    for h in hosts.hosts:
        flake_uri = str(h.meta.get("flake_uri", ".#"))
        if flake_uri not in flake_store_paths:
            res = subprocess.run(
                [
                    "nix",
                    "--extra-experimental-features",
                    "nix-command flakes",
                    "flake",
                    "metadata",
                    "--json",
                    flake_uri,
                ],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            data = json.loads(res.stdout)
            flake_store_paths[flake_uri] = data["path"]

    def deploy(h: Host) -> None:
        target = f"{h.user or 'root'}@{h.host}"
        flake_store_path = flake_store_paths[str(h.meta.get("flake_uri", ".#"))]
        flake_path = str(h.meta.get("flake_path", "/etc/nixos"))
        ssh_arg = f"-p {h.port}" if h.port else ""

        if h.host_key_check != HostKeyCheck.STRICT:
            ssh_arg += " -o StrictHostKeyChecking=no"
        if h.host_key_check == HostKeyCheck.NONE:
            ssh_arg += " -o UserKnownHostsFile=/dev/null"

        ssh_arg += " -i " + h.key if h.key else ""

        h.run_local(
            f"rsync --checksum -vaF --delete -e 'ssh {ssh_arg}' {flake_store_path}/ {target}:{flake_path}"
        )

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
                f"{flake_path}{flake_attr}",
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
    deploy_nixos(
        HostGroup(
            [Host(args.host, user=args.user, meta=dict(flake_attr=args.flake_attr))]
        )
    )


def register_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_mutually_exclusive_group(required=True)
    # TODO pass all args we don't parse into ssh_args, currently it fails if arg starts with -
    parser.add_argument("--flake-uri", type=str, default=".#", desc="nix flake uri")
    parser.add_argument(
        "--flake-attr", type=str, description="nixos configuration in the flake"
    )
    parser.add_argument("--user", type=str, default="root")
    parser.add_argument("host", type=str)
    parser.set_defaults(func=update)
