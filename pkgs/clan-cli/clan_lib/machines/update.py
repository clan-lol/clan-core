import json
import logging
import os
import re
import shlex
import uuid
from contextlib import ExitStack
from typing import TYPE_CHECKING, Literal, cast

from clan_cli.hyperlink import hyperlink_same_text_and_url
from clan_cli.vars.upload import upload_secret_vars

from clan_lib.api import API
from clan_lib.async_run import is_async_cancelled
from clan_lib.cmd import Log, MsgColor, RunOpts, run
from clan_lib.colors import AnsiColor
from clan_lib.errors import ClanCmdError, ClanError
from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_build, nix_command, nix_metadata
from clan_lib.ssh.localhost import LocalHost
from clan_lib.ssh.remote import Remote

if TYPE_CHECKING:
    from clan_lib.ssh.host import Host

log = logging.getLogger(__name__)


def _nix_options_from_machine(machine: Machine) -> list[str]:
    """Build the common nix CLI options from a Machine's flake config."""
    return [
        "--show-trace",
        "--option",
        "keep-going",
        "true",
        "--option",
        "accept-flake-config",
        "true",
        "-L",
        *(machine.flake.nix_options or []),
    ]


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


SshAuthContext = Literal["upload_sources", "copy_closure"]

_GUIDE_URL = "https://docs.clan.lol/guides/ssh-agent-forwarding"


def _check_ssh_auth_error(
    error: ClanError,
    machine: Machine,
    context: SshAuthContext,
    *,
    build_host: "Host | None" = None,
    target_host: "Host | None" = None,
) -> None:
    """Detect SSH authentication failures and print guidance.

    Only stderr is inspected, to avoid false positives from build output.

    ``context`` indicates which SSH hop failed and selects the guidance
    message:

    - ``"upload_sources"`` — workstation -> build host (during
      ``nix copy`` / ``nix flake archive`` of the flake sources).
    - ``"copy_closure"`` — build host -> target host (during the
      closure copy that runs after ``nix build``).

    ``build_host`` and ``target_host`` are the resolved SSH endpoints.
    When provided, their ``target`` strings (``user@address``) are shown
    in the guidance so users know exactly which hop failed.
    """
    if not isinstance(error, ClanCmdError):
        return

    stderr = error.cmd.stderr
    build_label = build_host.target if build_host is not None else "<build host>"
    target_label = target_host.target if target_host is not None else "<target host>"
    guide_link = hyperlink_same_text_and_url(_GUIDE_URL)
    host_key_link = hyperlink_same_text_and_url(f"{_GUIDE_URL}#host-key-verification")

    # 1) Host key verification failed — the remote's key is not in the
    #    relevant known_hosts file yet. Suggest --host-key-check
    #    accept-new, which propagates into NIX_SSHOPTS and lets the
    #    nested SSH trust the key on first use.
    if "Host key verification failed" in stderr:
        match context:
            case "copy_closure":
                machine.warn(
                    f"\nHost key verification failed while build host "
                    f"`{build_label}` tried to SSH into target host "
                    f"`{target_label}` to copy the system closure. The "
                    "target's host key is not in the build host's "
                    "`~/.ssh/known_hosts`, which is separate from your "
                    "workstation's.\n"
                    "\n"
                    "Re-run with `--host-key-check accept-new` to trust the "
                    "key on first use. Clan propagates the flag into the "
                    "nested SSH the build host opens to the target, so "
                    "first deploy succeeds and the key is recorded on the "
                    "build host for subsequent runs.\n"
                    "\n"
                    f"See {host_key_link} for details."
                )
            case "upload_sources":
                machine.warn(
                    f"\nHost key verification failed while connecting to build "
                    f"host `{build_label}` to upload flake sources. The "
                    "build host's key is not in your workstation's "
                    "`~/.ssh/known_hosts`.\n"
                    "\n"
                    "Re-run with `--host-key-check accept-new` to trust the "
                    "key on first use.\n"
                    "\n"
                    f"See {host_key_link} for details."
                )
        return

    # 2) SSH authentication failed (key not accepted on the remote).
    ssh_auth_indicators = [
        "Permission denied (publickey",
        "fatal: Could not read from remote repository",
    ]
    if not any(indicator in stderr for indicator in ssh_auth_indicators):
        return

    match context:
        case "copy_closure":
            machine.warn(
                f"\nSSH authentication from build host `{build_label}` to "
                f"target host `{target_label}` failed while copying the system "
                "closure.\n"
                "\n"
                "When `deploy.buildHost` is set, the build host opens its own SSH "
                "connection to the target host. That connection needs credentials "
                "the target host accepts.\n"
                "\n"
                "You have two options:\n"
                "\n"
                f"1. Install a dedicated SSH key on `{build_label}` and authorize "
                f"it on `{target_label}` (recommended).\n"
                "2. Enable SSH agent forwarding so the build host reuses your "
                "workstation's keys:\n"
                f"   - Per-machine: `inventory.machines.{machine.name}.deploy.forwardAgent = true;`\n"
                "   - Globally:    `clan.core.networking.forwardAgent = true;`\n"
                "\n"
                f"See {guide_link} for the full walkthrough."
            )
        case "upload_sources":
            machine.warn(
                f"\nSSH authentication to build host `{build_label}` failed while "
                "uploading flake sources.\n"
                "\n"
                "Verify that your local user can open a plain SSH session to the "
                "build host before retrying:\n"
                "\n"
                f"    ssh {build_label}\n"
                "\n"
                "If you deploy with a separate `deploy.buildHost`, see "
                f"{guide_link} for the recommended key setup."
            )


def upload_sources(machine: Machine, remote: Remote, upload_inputs: bool) -> str:
    """Upload the flake sources to a remote build host.

    This uses ``nix copy`` or ``nix flake archive`` to transfer the flake
    (and optionally its inputs) to the remote machine where the build will
    happen.  It must not be called when building locally — the sources are
    already present in that case.
    """
    env = remote.nix_ssh_env(os.environ.copy())

    flake_url = (
        str(machine.flake.path) if machine.flake.is_local else machine.flake.identifier
    )
    flake_data = nix_metadata(flake_url)
    has_path_inputs = any(
        is_local_input(node) for node in flake_data["locks"]["nodes"].values()
    )

    def _remote_url(scheme: str) -> str:
        remote_program_params = ""
        if machine._class_ == "darwin":
            if scheme == "ssh-ng":
                remote_program_params = (
                    "?remote-program=bash -lc 'exec nix-daemon --stdio'"
                )
            else:
                remote_program_params = (
                    "?remote-program=bash -lc 'exec nix-store --serve --write'"
                )
        return f"{remote.ssh_url(scheme=scheme)}{remote_program_params}"

    if not has_path_inputs and not upload_inputs:
        # Just copy the flake to the remote machine, we can substitute other inputs there.
        path = flake_data["path"]
        remote_url = _remote_url("ssh-ng")
        cmd = nix_command(
            [
                "copy",
                "--to",
                remote_url,
                "--no-check-sigs",
                path,
            ],
        )
        try:
            run(
                cmd,
                RunOpts(
                    env=env,
                    needs_user_terminal=True,
                    error_msg="failed to upload sources",
                    prefix=machine.name,
                ),
            )
        except ClanError as e:
            _check_ssh_auth_error(
                e, machine, context="upload_sources", build_host=remote
            )
            raise
        return path

    # Slow path: we need to upload all sources to the remote machine
    # Don't use ssh-ng here. It makes `flake archive` fail, despite root@..., with:
    #   cannot add path '/nix/store/...' because it lacks a signature by a trusted key
    # The issue is the missing `--no-check-sigs` option in `nix flake archive`.
    remote_url = _remote_url("ssh")
    cmd = nix_command(
        [
            "flake",
            "archive",
            "--to",
            remote_url,
            "--json",
            flake_url,
        ],
    )
    try:
        proc = run(
            cmd,
            RunOpts(
                env=env,
                needs_user_terminal=True,
                error_msg="failed to upload sources",
                prefix=machine.name,
            ),
        )
    except ClanError as e:
        _check_ssh_auth_error(e, machine, context="upload_sources", build_host=remote)
        raise

    try:
        return json.loads(proc.stdout)["path"]
    except (json.JSONDecodeError, OSError) as e:
        msg = f"failed to parse output of {shlex.join(cmd)}: {e}\nGot: {proc.stdout}"
        raise ClanError(msg) from e


def _nixos_build(
    machine: Machine,
    flake_store_path: str,
    build_host: "Host",
    nix_options: list[str],
) -> str:
    """Build the NixOS system toplevel on the build host.

    Returns the store path of the built system configuration.
    """
    attr = f'{flake_store_path}#nixosConfigurations."{machine.name}".config.system.build.toplevel'
    # local=False when the build runs on a remote host, so that
    # host-specific flags like --store (test suite) are omitted.
    cmd = nix_build([attr, *nix_options], local=not isinstance(build_host, Remote))

    ret = build_host.run(
        cmd,
        RunOpts(
            check=False,
            log=Log.BOTH,
            msg_color=MsgColor(stderr=AnsiColor.DEFAULT),
            needs_user_terminal=True,
            prefix=machine.name,
        ),
    )

    if is_async_cancelled():
        msg = "Build cancelled"
        raise ClanError(msg)

    if ret.returncode != 0:
        if "… while fetching the input" in ret.stderr:
            msg = (
                "Detected potential issue when fetching flake inputs on remote."
                "\nTry running the update with --update-inputs to prefetch inputs "
                "locally and upload them instead."
            )
            raise ClanError(msg)

        msg = f"nix build failed for '{machine.name}' (exit code {ret.returncode})."
        raise ClanError(msg)

    # nix build --print-out-paths outputs the store path to stdout
    config_path = ""
    for line in reversed(ret.stdout.splitlines()):
        stripped = line.strip()
        if stripped.startswith("/nix/store/"):
            config_path = stripped
            break

    if not config_path:
        msg = (
            f"Could not find /nix/store path in nix build output.\n"
            f"stdout: {ret.stdout!r}"
        )
        raise ClanError(msg)

    return config_path


def _copy_closure(
    config_path: str,
    build_host: "Host",
    target_host: "Host",
    machine_name: str,
    extra_env: dict[str, str] | None = None,
) -> None:
    """Copy the system closure from the build host to the target host.

    Only needed when the build host differs from the target host.
    """
    if not isinstance(target_host, Remote):
        # Target is local — the store path should already be present
        return

    target_url = target_host.ssh_url(scheme="ssh-ng")
    # local=False when the copy runs on a remote build host, so that
    # host-specific flags like --store (test suite) are omitted.
    cmd = nix_command(
        [
            "copy",
            "--to",
            target_url,
            "--no-check-sigs",
            config_path,
        ],
        local=not isinstance(build_host, Remote),
    )

    build_host.run(
        cmd,
        RunOpts(
            log=Log.BOTH,
            needs_user_terminal=True,
            error_msg=f"failed to copy closure to {target_host.target}",
            prefix=machine_name,
        ),
        extra_env=extra_env,
    )


def _nixos_activate(
    config_path: str,
    target_host_root: "Host",
    machine_name: str,
    install_bootloader: bool = False,
    specialisation: str | None = None,
) -> None:
    """Set the system profile and run switch-to-configuration on the target.

    Uses ``systemd-run --pipe --quiet`` so the activation survives SSH
    connection drops, while still streaming stdout/stderr back to us
    directly (no background ``journalctl`` relay, no race condition).
    ``--quiet`` only suppresses systemd-run's own status lines; the
    unit's output flows through ``--pipe`` unaffected.
    """
    # Verify the build output looks like a valid NixOS system before
    # committing it to the profile.  nixos-rebuild checks for
    # ``nixos-version``. We replicate that safety check here.
    ret = target_host_root.run(
        ["test", "-e", f"{config_path}/nixos-version"],
        RunOpts(check=False, prefix=machine_name),
    )
    if ret.returncode != 0:
        msg = (
            f"The build output at {config_path} does not look like a valid "
            f"NixOS system configuration (missing nixos-version). "
            f"Refusing to activate."
        )
        raise ClanError(msg)

    # Set the system profile so the new generation survives a reboot.
    target_host_root.run(
        [
            "nix-env",
            "-p",
            "/nix/var/nix/profiles/system",
            "--set",
            config_path,
        ],
        RunOpts(
            log=Log.BOTH,
            prefix=machine_name,
        ),
    )

    # Build the systemd-run wrapper command.
    # --pipe:    connect unit's stdin/stdout/stderr to our own, so output
    #            is streamed directly — no need for a journalctl sidecar.
    # --wait:    block until the unit finishes (implicit with --pipe).
    # --quiet:   suppress systemd-run's own status lines (runtime, CPU,
    #            memory, etc.); the unit's stdout/stderr still flows
    #            through --pipe unaffected.
    # --collect: remove the transient unit after it finishes.
    # Include a random suffix to avoid conflicts with a previous run that
    # may still be shutting down (e.g. after Ctrl-C).
    def switch_cmd(unit: str) -> list[str]:
        return [
            "systemd-run",
            "--pipe",
            "--wait",
            "--quiet",
            "--collect",
            "--no-ask-password",
            "--service-type=exec",
            f"--unit={unit}",
            "-E",
            "LOCALE_ARCHIVE",
            # NIXOS_NO_CHECK=1 overrides switch inhibitors — safety checks
            # that block activation when critical components (e.g. systemd)
            # changed between generations.  Forwarded so users can force a
            # switch instead of rebooting.
            "-E",
            "NIXOS_NO_CHECK",
            "-E",
            f"NIXOS_INSTALL_BOOTLOADER={'1' if install_bootloader else '0'}",
            "--",
            f"{f'{config_path}/specialisation/{specialisation}' if specialisation else config_path}/bin/switch-to-configuration",
            "switch",
        ]

    unit_name = f"clan-switch-{machine_name}-{uuid.uuid4().hex[:8]}"
    ret = target_host_root.run(
        switch_cmd(unit_name),
        RunOpts(
            check=False,
            log=Log.BOTH,
            prefix=machine_name,
        ),
    )

    if ret.returncode == 0:
        return

    # First attempt failed — could be SSH drop or real failure.
    # Retry once (switch-to-configuration is idempotent).
    log.info(
        "[%s] activation returned %d — retrying",
        machine_name,
        ret.returncode,
    )
    last_unit = f"clan-switch-{machine_name}-{uuid.uuid4().hex[:8]}"
    ret = target_host_root.run(
        switch_cmd(last_unit),
        RunOpts(
            check=False,
            log=Log.BOTH,
            prefix=machine_name,
        ),
    )
    if ret.returncode == 0:
        return

    # Both attempts reported failure.  Fetch the journal for diagnostics.
    journal_output = ""
    try:
        journal_ret = target_host_root.run(
            [
                "journalctl",
                "--no-pager",
                "-n",
                "50",
                "-u",
                last_unit,
            ],
            RunOpts(check=False, prefix=machine_name),
        )
        if journal_ret.returncode == 0 and journal_ret.stdout.strip():
            journal_output = (
                f"\n\nJournal output from unit '{last_unit}':\n{journal_ret.stdout}"
            )
    except OSError:
        log.debug("[%s] failed to fetch journal for unit %s", machine_name, last_unit)

    # Final check: the activation may have actually succeeded despite SSH
    # reporting failure (e.g. connection dropped after activation finished).
    check = target_host_root.run(
        ["readlink", "/run/current-system"],
        RunOpts(check=False, prefix=machine_name),
    )
    if check.returncode == 0 and check.stdout.strip() == config_path:
        log.info(
            "[%s] target is already running %s — activation succeeded",
            machine_name,
            config_path,
        )
        return

    msg = (
        f"switch-to-configuration failed on '{machine_name}' "
        f"(exit code {ret.returncode}).{journal_output or ' See above for details.'}"
    )
    raise ClanError(msg)


@API.register
def run_machine_update(
    machine: Machine,
    target_host: Remote | LocalHost,
    build_host: Remote | LocalHost | None = None,
    upload_inputs: bool = False,
    specialisation: str | None = None,
) -> None:
    """Update an existing machine.

    For NixOS machines the build → copy → profile → activate pipeline is
    executed directly (no nixos-rebuild).  Darwin machines still use
    darwin-rebuild.

    Args:
        machine: The Machine instance to deploy.
        target_host: Remote object representing the target host for deployment.
        build_host: Optional Remote object representing the build host.
        upload_inputs: Whether to upload flake inputs from the local.
        specialisation: Activates given specialisation

    Raises:
        ClanError: If the machine is not found in the inventory or if there are issues with
            generating vars.

    """
    with ExitStack() as stack:
        _target_host: Host = cast(
            "Host", stack.enter_context(target_host.host_connection())
        )
        _build_host: Host
        # If no build host is specified, use the target host as the build host.
        if build_host is None:
            _build_host = _target_host
        else:
            _build_host = cast(
                "Host", stack.enter_context(build_host.host_connection())
            )

        # Some operations require root privileges on the target host.
        target_host_root = stack.enter_context(_target_host.become_root())

        # Upload secrets to the target host using root
        upload_secret_vars(machine, target_host_root)

        # Upload the flake's source to the build host.  When building
        # locally the sources are already present, so we only need the
        # flake store path for the --flake argument.
        if isinstance(_build_host, Remote):
            flake_store_path = upload_sources(machine, _build_host, upload_inputs)
        else:
            flake_url = (
                str(machine.flake.path)
                if machine.flake.is_local
                else machine.flake.identifier
            )
            flake_store_path = nix_metadata(flake_url)["path"]

        if machine._class_ == "nixos":
            _update_nixos(
                machine=machine,
                flake_store_path=flake_store_path,
                build_host=_build_host,
                target_host=_target_host,
                target_host_root=target_host_root,
                specialisation=specialisation,
            )
        elif machine._class_ == "darwin":
            _update_darwin(
                machine=machine,
                flake_store_path=flake_store_path,
                build_host=_build_host,
                target_host=_target_host,
                target_host_root=target_host_root,
            )
        else:
            msg = f"Unsupported machine type: {machine._class_}\n\nUpdate for this type is not handled yet.\n"
            raise ClanError(msg)


def _update_nixos(
    machine: Machine,
    flake_store_path: str,
    build_host: "Host",
    target_host: "Host",
    target_host_root: "Host",
    specialisation: str | None,
) -> None:
    """Build → copy → profile → activate pipeline for NixOS machines."""
    nix_options = _nix_options_from_machine(machine)

    # If we build on the target host, we need to become root for building.
    # We are not using --use-remote-sudo here, so that our sudo ask proxy
    # works: https://git.clan.lol/clan/clan-core/pulls/3642
    if build_host is target_host:
        build_host = target_host_root

    # 1. Build — no NIX_SSHOPTS needed, nix build doesn't SSH anywhere.
    config_path = _nixos_build(
        machine=machine,
        flake_store_path=flake_store_path,
        build_host=build_host,
        nix_options=nix_options,
    )

    if is_async_cancelled():
        return

    # 2. Copy closure to target (only when build host ≠ target host).
    #    NIX_SSHOPTS carries the SSH options that ``nix copy`` needs to
    #    reach the target (e.g. ProxyCommand for iroh/tor).
    if build_host is not target_host_root:
        copy_env: dict[str, str] | None = (
            target_host.nix_ssh_env(control_master=False)
            if isinstance(target_host, Remote)
            else None
        )
        try:
            _copy_closure(
                config_path=config_path,
                build_host=build_host,
                target_host=target_host_root,
                machine_name=machine.name,
                extra_env=copy_env,
            )
        except ClanError as e:
            _check_ssh_auth_error(
                e,
                machine,
                context="copy_closure",
                build_host=build_host,
                target_host=target_host_root,
            )
            raise

    if is_async_cancelled():
        return

    # 3 + 4. Set profile and activate
    _nixos_activate(
        config_path, target_host_root, machine.name, specialisation=specialisation
    )


def _build_darwin_rebuild_cmd(
    machine_name: str,
    flake_store_path: str,
    nix_options: list[str],
) -> list[str]:
    """Build the darwin-rebuild switch command.

    The flake reference must use plain ``#name`` syntax without extra quotes,
    because ``darwin-rebuild`` passes the value directly to Nix which does not
    expect shell-level quoting inside the fragment.
    """
    return [
        "/run/current-system/sw/bin/darwin-rebuild",
        "switch",
        *nix_options,
        "--flake",
        f"{flake_store_path}#{machine_name}",
    ]


def _update_darwin(
    machine: Machine,
    flake_store_path: str,
    build_host: "Host",
    target_host: "Host",
    target_host_root: "Host",
) -> None:
    """Darwin machines still use darwin-rebuild."""
    nix_options = _nix_options_from_machine(machine)

    if build_host is target_host:
        build_host = target_host_root

    extra_env: dict[str, str] | None = None
    if isinstance(build_host, Remote):
        extra_env = build_host.nix_ssh_env(control_master=False)

    switch_cmd = _build_darwin_rebuild_cmd(machine.name, flake_store_path, nix_options)

    build_host.run(
        switch_cmd,
        RunOpts(
            log=Log.BOTH,
            msg_color=MsgColor(stderr=AnsiColor.DEFAULT),
            needs_user_terminal=True,
            prefix=machine.name,
        ),
        extra_env=extra_env,
    )
