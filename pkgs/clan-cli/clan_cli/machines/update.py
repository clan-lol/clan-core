import argparse
import json
import logging
import os
import re
import shlex
import sys
from contextlib import ExitStack

from clan_lib.api import API

from clan_cli.async_run import AsyncContext, AsyncOpts, AsyncRuntime, is_async_cancelled
from clan_cli.cmd import MsgColor, RunOpts, run
from clan_cli.colors import AnsiColor
from clan_cli.completions import (
    add_dynamic_completer,
    complete_machines,
)
from clan_cli.errors import ClanError
from clan_cli.facts.generate import generate_facts
from clan_cli.facts.upload import upload_secrets
from clan_cli.flake import Flake
from clan_cli.inventory import Machine as InventoryMachine
from clan_cli.machines.machines import Machine
from clan_cli.nix import nix_command, nix_config, nix_metadata
from clan_cli.ssh.host import Host, HostKeyCheck
from clan_cli.vars.generate import generate_vars
from clan_cli.vars.upload import upload_secret_vars

from .inventory import get_all_machines, get_selected_machines

log = logging.getLogger(__name__)


def is_local_input(node: dict[str, dict[str, str]]) -> bool:
    locked = node.get("locked")
    if not locked:
        return False
    # matches path and git+file://
    return (
        locked["type"] == "path"
        # local vcs inputs i.e. git+file:///
        or re.match(r"^file://", locked.get("url", "")) is not None
    )


def upload_sources(machine: Machine, host: Host) -> str:
    env = host.nix_ssh_env(os.environ.copy())

    flake_url = (
        str(machine.flake.path) if machine.flake.is_local else machine.flake.identifier
    )
    flake_data = nix_metadata(flake_url)
    has_path_inputs = any(
        is_local_input(node) for node in flake_data["locks"]["nodes"].values()
    )

    if not has_path_inputs:
        # Just copy the flake to the remote machine, we can substitute other inputs there.
        path = flake_data["path"]
        cmd = nix_command(
            [
                "copy",
                "--to",
                f"ssh://{host.target}",
                "--no-check-sigs",
                path,
            ]
        )
        run(
            cmd,
            RunOpts(
                env=env,
                needs_user_terminal=True,
                error_msg="failed to upload sources",
                prefix=machine.name,
            ),
        )
        return path

    # Slow path: we need to upload all sources to the remote machine
    cmd = nix_command(
        [
            "flake",
            "archive",
            "--to",
            f"ssh://{host.target}",
            "--json",
            flake_url,
        ]
    )
    proc = run(
        cmd,
        RunOpts(
            env=env, needs_user_terminal=True, error_msg="failed to upload sources"
        ),
    )

    try:
        return json.loads(proc.stdout)["path"]
    except (json.JSONDecodeError, OSError) as e:
        msg = f"failed to parse output of {shlex.join(cmd)}: {e}\nGot: {proc.stdout}"
        raise ClanError(msg) from e


@API.register
def update_machines(base_path: str, machines: list[InventoryMachine]) -> None:
    group_machines: list[Machine] = []

    # Convert InventoryMachine to Machine
    flake = Flake(base_path)
    for machine in machines:
        name = machine.get("name")
        if not name:
            msg = "Machine name is not set"
            raise ClanError(msg)
        m = Machine(
            name,
            flake=flake,
        )
        # prefer target host set via inventory, but fallback to the one set in the machine
        if target_host := machine.get("deploy", {}).get("targetHost"):
            m.override_target_host = target_host
        group_machines.append(m)

    deploy_machines(group_machines)


def deploy_machine(machine: Machine) -> None:
    with ExitStack() as stack:
        target_host = stack.enter_context(machine.target_host())
        build_host = stack.enter_context(machine.build_host())

        if machine._class_ == "darwin":
            if not machine.deploy_as_root and target_host.user == "root":
                msg = f"'targetHost' should be set to a non-root user for deploying to nix-darwin on machine '{machine.name}'"
                raise ClanError(msg)

        host = build_host or target_host

        generate_facts([machine], service=None, regenerate=False)
        generate_vars([machine], generator_name=None, regenerate=False)

        upload_secrets(machine, target_host)
        upload_secret_vars(machine, target_host)

        path = upload_sources(machine, host)

        nix_options = [
            "--show-trace",
            "--option",
            "keep-going",
            "true",
            "--option",
            "accept-flake-config",
            "true",
            "-L",
            *machine.nix_options,
            "--flake",
            f"{path}#{machine.name}",
        ]

        become_root = machine.deploy_as_root

        if machine._class_ == "nixos":
            nix_options += [
                "--fast",
                "--build-host",
                "",
            ]

            if build_host:
                become_root = False
                nix_options += ["--target-host", build_host.target]

                if target_host.user != "root":
                    nix_options += ["--use-remote-sudo"]

        switch_cmd = [f"{machine._class_}-rebuild", "switch", *nix_options]
        test_cmd = [f"{machine._class_}-rebuild", "test", *nix_options]

        env = host.nix_ssh_env(None)
        ret = host.run(
            switch_cmd,
            RunOpts(check=False, msg_color=MsgColor(stderr=AnsiColor.DEFAULT)),
            extra_env=env,
            become_root=become_root,
        )

        # Last output line (config store path) is printed to stdout instead of stderr
        lines = ret.stdout.splitlines()
        if lines:
            print(lines[-1])

        if is_async_cancelled():
            return

        # retry nixos-rebuild switch if the first attempt failed
        if ret.returncode != 0:
            is_mobile = machine.deployment.get("nixosMobileWorkaround", False)
            # if the machine is mobile, we retry to deploy with the mobile workaround method
            if is_mobile:
                machine.info(
                    "Mobile machine detected, applying workaround deployment method"
                )
            ret = host.run(
                test_cmd if is_mobile else switch_cmd,
                RunOpts(
                    msg_color=MsgColor(stderr=AnsiColor.DEFAULT),
                    needs_user_terminal=True,
                ),
                extra_env=env,
                become_root=become_root,
            )


def deploy_machines(machines: list[Machine]) -> None:
    """
    Deploy to all hosts in parallel
    """

    with AsyncRuntime() as runtime:
        for machine in machines:
            runtime.async_run(
                AsyncOpts(
                    tid=machine.name, async_ctx=AsyncContext(prefix=machine.name)
                ),
                deploy_machine,
                machine,
            )
        runtime.join_all()
        runtime.check_all()


def update_command(args: argparse.Namespace) -> None:
    try:
        if args.flake is None:
            msg = "Could not find clan flake toplevel directory"
            raise ClanError(msg)
        machines = []
        if len(args.machines) == 1 and args.target_host is not None:
            machine = Machine(
                name=args.machines[0], flake=args.flake, nix_options=args.option
            )
            machine.override_target_host = args.target_host
            machine.override_build_host = args.build_host
            machine.host_key_check = HostKeyCheck.from_str(args.host_key_check)
            machines.append(machine)

        elif args.target_host is not None:
            print("target host can only be specified for a single machine")
            exit(1)
        else:
            if len(args.machines) == 0:
                ignored_machines = []
                for machine in get_all_machines(args.flake, args.option):
                    if machine.deployment.get("requireExplicitUpdate", False):
                        continue
                    try:
                        machine.build_host  # noqa: B018
                    except ClanError:  # check if we have a build host set
                        ignored_machines.append(machine)
                        continue
                    machine.host_key_check = HostKeyCheck.from_str(args.host_key_check)
                    machine.override_build_host = args.build_host
                    machines.append(machine)

                if not machines and ignored_machines != []:
                    print(
                        "WARNING: No machines to update."
                        "The following defined machines were ignored because they"
                        "do not have the `clan.core.networking.targetHost` nixos option set:",
                        file=sys.stderr,
                    )
                    for machine in ignored_machines:
                        print(machine, file=sys.stderr)

            else:
                machines = get_selected_machines(args.flake, args.option, args.machines)
                for machine in machines:
                    machine.override_build_host = args.build_host
                    machine.host_key_check = HostKeyCheck.from_str(args.host_key_check)

        config = nix_config()
        system = config["system"]
        machine_names = [machine.name for machine in machines]
        args.flake.precache(
            [
                f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.clan.core.vars.generators.*.validationHash",
                f"clanInternals.machines.{system}.{{{','.join(machine_names)}}}.config.system.clan.deployment.file",
            ]
        )

        deploy_machines(machines)
    except KeyboardInterrupt:
        log.warning("Interrupted by user")
        sys.exit(1)


def register_update_parser(parser: argparse.ArgumentParser) -> None:
    machines_parser = parser.add_argument(
        "machines",
        type=str,
        nargs="*",
        default=[],
        metavar="MACHINE",
        help="Machine to update. If no machines are specified, all machines that don't require explicit updates will be updated.",
    )
    add_dynamic_completer(machines_parser, complete_machines)

    parser.add_argument(
        "--host-key-check",
        choices=["strict", "ask", "tofu", "none"],
        default="ask",
        help="Host key (.ssh/known_hosts) check mode.",
    )
    parser.add_argument(
        "--target-host",
        type=str,
        help="Address of the machine to update, in the format of user@host:1234.",
    )
    parser.add_argument(
        "--build-host",
        type=str,
        help="Address of the machine to build the flake, in the format of user@host:1234.",
    )
    parser.set_defaults(func=update_command)
