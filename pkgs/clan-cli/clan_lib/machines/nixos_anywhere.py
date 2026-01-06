"""Common utilities for nixos-anywhere command building.

This module provides helper functions for building nixos-anywhere commands
used by both install.py and hardware.py. Each function is designed to be
called in any order, allowing callers to preserve their specific execution
sequences.
"""

import os
from pathlib import Path

from clan_lib.machines.machines import Machine
from clan_lib.nix import nix_shell
from clan_lib.ssh.create import SSHKeyPair, create_secret_key_nixos_anywhere
from clan_lib.ssh.remote import Remote


def setup_environ(target_host: Remote) -> dict[str, str]:
    """Create environment dict, setting SSHPASS if password is present.

    Args:
        target_host: Remote target with optional password

    Returns:
        Copy of os.environ with SSHPASS set if password exists

    """
    environ = os.environ.copy()
    if target_host.password:
        environ["SSHPASS"] = target_host.password
    return environ


def add_password_options(cmd: list[str], target_host: Remote) -> list[str]:
    """Add password authentication options if password is set.

    Adds: --env-password --ssh-option IdentitiesOnly=yes

    Args:
        cmd: Command list to extend
        target_host: Remote target with optional password

    Returns:
        Extended command list (new list, original unchanged)

    """
    if target_host.password:
        return [*cmd, "--env-password", "--ssh-option", "IdentitiesOnly=yes"]
    return cmd


def add_target_private_key(cmd: list[str], target_host: Remote) -> list[str]:
    """Add SSH IdentityFile option for target's private key.

    Adds: --ssh-option IdentityFile={private_key}

    Args:
        cmd: Command list to extend
        target_host: Remote target with optional private_key

    Returns:
        Extended command list (new list, original unchanged)

    """
    if target_host.private_key:
        return [*cmd, "--ssh-option", f"IdentityFile={target_host.private_key}"]
    return cmd


def add_ssh_port(cmd: list[str], target_host: Remote) -> list[str]:
    """Add SSH port option if port is set.

    Adds: --ssh-port {port}

    Args:
        cmd: Command list to extend
        target_host: Remote target with optional port

    Returns:
        Extended command list (new list, original unchanged)

    """
    if target_host.port:
        return [*cmd, "--ssh-port", str(target_host.port)]
    return cmd


def add_nixos_anywhere_key(
    cmd: list[str],
    priv_key: Path | None = None,
) -> tuple[list[str], SSHKeyPair]:
    """Create or use existing nixos-anywhere SSH key and add to command.

    Adds: -i {private_key_path}

    Args:
        cmd: Command list to extend
        priv_key: Optional existing private key path. If None, creates new key.

    Returns:
        Tuple of (extended command list, SSHKeyPair)

    """
    if priv_key is None:
        key_pair = create_secret_key_nixos_anywhere()
    else:
        key_pair = SSHKeyPair(private=priv_key, public=priv_key.with_suffix(".pub"))
    return [*cmd, "-i", str(key_pair.private)], key_pair


def add_debug(cmd: list[str], debug: bool) -> list[str]:
    """Add debug flag if enabled.

    Adds: --debug

    Args:
        cmd: Command list to extend
        debug: Whether to enable debug mode

    Returns:
        Extended command list (new list, original unchanged)

    """
    if debug:
        return [*cmd, "--debug"]
    return cmd


def add_kexec(cmd: list[str], kexec: str | None) -> list[str]:
    """Add kexec image URL if specified.

    Adds: --kexec {url}

    Args:
        cmd: Command list to extend
        kexec: Optional kexec image URL

    Returns:
        Extended command list (new list, original unchanged)

    """
    if kexec:
        return [*cmd, "--kexec", kexec]
    return cmd


def add_test_store_workaround(cmd: list[str], environ: dict[str, str]) -> list[str]:
    """Add workaround for test store when CLAN_TEST_STORE is set.

    REMOVEME when nixos-anywhere > 1.12.0
    In 1.12.0 and earlier, nixos-anywhere doesn't pass Nix options when
    attempting to get substituters which leads to the installation test
    failing with the error of not being able to substitute flake-parts.
    See: https://github.com/nix-community/nixos-anywhere/pull/596

    Adds: --no-use-machine-substituters

    Args:
        cmd: Command list to extend
        environ: Environment dict to check for CLAN_TEST_STORE

    Returns:
        Extended command list (new list, original unchanged)

    """
    if "CLAN_TEST_STORE" in environ:
        return [*cmd, "--no-use-machine-substituters"]
    return cmd


def add_nix_options(cmd: list[str], machine: Machine) -> list[str]:
    """Extend command with machine's flake nix options.

    Args:
        cmd: Command list to extend
        machine: Machine with flake containing nix_options

    Returns:
        Extended command list (new list, original unchanged)

    """
    return [*cmd, *(machine.flake.nix_options or [])]


def add_target(cmd: list[str], target_host: Remote) -> list[str]:
    """Append target host address to command.

    Args:
        cmd: Command list to extend
        target_host: Remote target

    Returns:
        Extended command list (new list, original unchanged)

    """
    return [*cmd, target_host.target]


def wrap_nix_shell(cmd: list[str], target_host: Remote) -> list[str]:
    """Wrap command with nix_shell, handling socks proxy if needed.

    Args:
        cmd: The nixos-anywhere command to wrap
        target_host: Remote target (may have socks_port set)

    Returns:
        Command wrapped with appropriate nix_shell invocation

    """
    if target_host.socks_port:
        wrapper = target_host.socks_wrapper
        wrapper_cmd = wrapper.cmd if wrapper else []
        wrapper_packages = wrapper.packages if wrapper else []
        return nix_shell(
            ["nixos-anywhere", *wrapper_packages],
            [*wrapper_cmd, *cmd],
        )
    return nix_shell(["nixos-anywhere"], cmd)
