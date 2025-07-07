import json
import logging
import os
import re
import shlex
from contextlib import ExitStack

from clan_cli.facts.generate import generate_facts
from clan_cli.facts.upload import upload_secrets
from clan_cli.vars.generate import generate_vars
from clan_cli.vars.upload import upload_secret_vars

from clan_lib.api import API
from clan_lib.async_run import is_async_cancelled
from clan_lib.cmd import Log, MsgColor, RunOpts, run
from clan_lib.colors import AnsiColor
from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_command, nix_metadata
from clan_lib.ssh.remote import Remote

log = logging.getLogger(__name__)


def is_local_input(node: dict[str, dict[str, str]]) -> bool:
    locked = node.get("locked")
    if not locked:
        return False
    # matches path and git+file://
    local = (
        locked["type"] == "path"
        # local vcs inputs i.e. git+file:///
        or re.match(r"^file://", locked.get("url", "")) is not None
    )
    if local:
        print(f"[WARN] flake input has local node: {json.dumps(node)}")
    return local


def upload_sources(machine: Machine, ssh: Remote) -> str:
    env = ssh.nix_ssh_env(os.environ.copy())

    flake_url = (
        str(machine.flake.path) if machine.flake.is_local else machine.flake.identifier
    )
    flake_data = nix_metadata(flake_url)
    has_path_inputs = any(
        is_local_input(node) for node in flake_data["locks"]["nodes"].values()
    )

    # Construct the remote URL with proper parameters for Darwin
    remote_url = f"ssh-ng://{ssh.target}"
    # MacOS doesn't come with a proper login shell for ssh and therefore doesn't have nix in $PATH as it doesn't source /etc/profile
    if machine._class_ == "darwin":
        remote_url += "?remote-program=bash -lc 'exec nix-daemon --stdio'"

    if not has_path_inputs:
        # Just copy the flake to the remote machine, we can substitute other inputs there.
        path = flake_data["path"]
        cmd = nix_command(
            [
                "copy",
                "--to",
                remote_url,
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
            remote_url,
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
def run_machine_deploy(
    machine: Machine, target_host: Remote, build_host: Remote | None
) -> None:
    """Update an existing machine using nixos-rebuild or darwin-rebuild.
    Args:
        machine: The Machine instance to deploy.
        target_host: Remote object representing the target host for deployment.
        build_host: Optional Remote object representing the build host.
    Raises:
        ClanError: If the machine is not found in the inventory or if there are issues with
            generating facts or variables.
    """

    with ExitStack() as stack:
        target_host = stack.enter_context(target_host.ssh_control_master())

        if build_host is not None:
            build_host = stack.enter_context(build_host.ssh_control_master())

        host = build_host or target_host

        sudo_host = stack.enter_context(target_host.become_root())

        generate_facts([machine], service=None, regenerate=False)
        generate_vars([machine], generator_name=None, regenerate=False)

        upload_secrets(machine, sudo_host)
        upload_secret_vars(machine, sudo_host)

        path = upload_sources(machine, sudo_host)

        nix_options = machine.flake.nix_options if machine.flake.nix_options else []

        nix_options = [
            "--show-trace",
            "--option",
            "keep-going",
            "true",
            "--option",
            "accept-flake-config",
            "true",
            "-L",
            *nix_options,
            "--flake",
            f"{path}#{machine.name}",
        ]

        become_root = True

        if machine._class_ == "nixos":
            nix_options += [
                "--fast",
                "--build-host",
                "",
            ]

            if build_host:
                become_root = False
                nix_options += ["--target-host", target_host.target]

                if target_host.user != "root":
                    nix_options += ["--use-remote-sudo"]
            switch_cmd = ["nixos-rebuild", "switch", *nix_options]
        elif machine._class_ == "darwin":
            # use absolute path to darwin-rebuild
            switch_cmd = [
                "/run/current-system/sw/bin/darwin-rebuild",
                "switch",
                *nix_options,
            ]

        if become_root:
            host = sudo_host

        remote_env = host.nix_ssh_env(control_master=False)
        ret = host.run(
            switch_cmd,
            RunOpts(
                check=False,
                log=Log.BOTH,
                msg_color=MsgColor(stderr=AnsiColor.DEFAULT),
                needs_user_terminal=True,
            ),
            extra_env=remote_env,
        )

        if is_async_cancelled():
            return

        # retry nixos-rebuild switch if the first attempt failed
        if ret.returncode != 0:
            try:
                is_mobile = machine.select(
                    "config.system.clan.deployment.nixosMobileWorkaround"
                )
            except Exception:
                is_mobile = False
            # if the machine is mobile, we retry to deploy with the mobile workaround method
            if is_mobile:
                machine.info(
                    "Mobile machine detected, applying workaround deployment method"
                )
            ret = host.run(
                ["nixos--rebuild", "test", *nix_options] if is_mobile else switch_cmd,
                RunOpts(
                    log=Log.BOTH,
                    msg_color=MsgColor(stderr=AnsiColor.DEFAULT),
                    needs_user_terminal=True,
                ),
                extra_env=remote_env,
            )
