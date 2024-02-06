import argparse
import json
import logging
import os
import shlex
import subprocess
import sys
from pathlib import Path

from ..cmd import run
from ..errors import ClanError
from ..machines.machines import Machine
from ..nix import nix_build, nix_command, nix_config, nix_metadata
from ..secrets.generate import generate_secrets
from ..secrets.upload import upload_secrets
from ..ssh import Host, HostGroup, HostKeyCheck, parse_deployment_address

log = logging.getLogger(__name__)


def is_path_input(node: dict[str, dict[str, str]]) -> bool:
    locked = node.get("locked")
    if not locked:
        return False
    return locked["type"] == "path" or locked.get("url", "").startswith("file://")


def upload_sources(
    flake_url: str, remote_url: str, always_upload_source: bool = False
) -> str:
    if not always_upload_source:
        flake_data = nix_metadata(flake_url)
        url = flake_data["resolvedUrl"]
        has_path_inputs = any(
            is_path_input(node) for node in flake_data["locks"]["nodes"].values()
        )
        if not has_path_inputs and not is_path_input(flake_data):
            # No need to upload sources, we can just build the flake url directly
            # FIXME: this might fail for private repositories?
            return url
        if not has_path_inputs:
            # Just copy the flake to the remote machine, we can substitute other inputs there.
            path = flake_data["path"]
            env = os.environ.copy()
            # env["NIX_SSHOPTS"] = " ".join(opts.remote_ssh_options)
            assert remote_url
            cmd = nix_command(
                [
                    "copy",
                    "--to",
                    f"ssh://{remote_url}",
                    "--no-check-sigs",
                    path,
                ]
            )
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, env=env, check=False)
            if proc.returncode != 0:
                raise ClanError(
                    f"failed to upload sources: {shlex.join(cmd)} failed with {proc.returncode}"
                )
            return path

    # Slow path: we need to upload all sources to the remote machine
    assert remote_url
    cmd = nix_command(
        [
            "flake",
            "archive",
            "--to",
            f"ssh://{remote_url}",
            "--json",
            flake_url,
        ]
    )
    log.info("run %s", shlex.join(cmd))
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        raise ClanError(
            f"failed to upload sources: {shlex.join(cmd)} failed with {proc.returncode}"
        )
    try:
        return json.loads(proc.stdout)["path"]
    except (json.JSONDecodeError, OSError) as e:
        raise ClanError(
            f"failed to parse output of {shlex.join(cmd)}: {e}\nGot: {proc.stdout.decode('utf-8', 'replace')}"
        )


def deploy_nixos(hosts: HostGroup) -> None:
    """
    Deploy to all hosts in parallel
    """

    def deploy(h: Host) -> None:
        target = f"{h.user or 'root'}@{h.host}"
        ssh_arg = f"-p {h.port}" if h.port else ""
        env = os.environ.copy()
        env["NIX_SSHOPTS"] = ssh_arg
        path = upload_sources(".", target)

        if h.host_key_check != HostKeyCheck.STRICT:
            ssh_arg += " -o StrictHostKeyChecking=no"
        if h.host_key_check == HostKeyCheck.NONE:
            ssh_arg += " -o UserKnownHostsFile=/dev/null"

        ssh_arg += " -i " + h.key if h.key else ""

        machine: Machine = h.meta["machine"]

        generate_secrets(machine)
        upload_secrets(machine)

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
            f"{path}#{machine.name}",
        ]
        if target_host := h.meta.get("target_host"):
            target_host = f"{target_host.user or 'root'}@{target_host.host}"
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
    ignored_machines = []
    for name, machine_data in machines.items():
        if machine_data.get("requireExplicitUpdate", False):
            continue

        machine = Machine(name=name, flake=clan_dir, deployment_info=machine_data)
        try:
            hosts.append(machine.build_host)
        except ClanError:
            ignored_machines.append(name)
            continue
    if not hosts and ignored_machines != []:
        print(
            "WARNING: No machines to update. The following defined machines were ignored because they do not have `clan.networking.targetHost` nixos option set:",
            file=sys.stderr,
        )
        for machine in ignored_machines:
            print(machine, file=sys.stderr)
    # very hacky. would be better to do a MachinesGroup instead
    return HostGroup(hosts)


def get_selected_machines(machine_names: list[str], flake_dir: Path) -> HostGroup:
    hosts = []
    for name in machine_names:
        machine = Machine(name=name, flake=flake_dir)
        hosts.append(machine.build_host)
    return HostGroup(hosts)


# FIXME: we want some kind of inventory here.
def update(args: argparse.Namespace) -> None:
    if args.flake is None:
        raise ClanError("Could not find clan flake toplevel directory")
    if len(args.machines) == 1 and args.target_host is not None:
        machine = Machine(name=args.machines[0], flake=args.flake)
        machine.target_host_address = args.target_host
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

    deploy_nixos(machines)


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
