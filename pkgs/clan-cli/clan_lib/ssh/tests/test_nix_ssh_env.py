"""Tests for Remote.nix_ssh_env() and SSH option shell-quoting.

Nix tools (nix-copy-closure, nix copy, nix flake archive) parse
NIX_SSHOPTS with ``shellSplitString`` which honours shell quoting.
These tests verify that option values containing spaces are correctly
quoted so they survive the split.
"""

import shlex
from pathlib import Path
from tempfile import TemporaryDirectory

from clan_lib.ssh.remote import Remote


def _parse_nix_sshopts(env: dict[str, str]) -> list[str]:
    """Simulate how Nix parses NIX_SSHOPTS (shell split)."""
    return shlex.split(env["NIX_SSHOPTS"])


def test_nix_ssh_env_proxy_command_with_spaces() -> None:
    """ProxyCommand with spaces must survive Nix's shellSplitString."""
    remote = Remote(
        address="myhost",
        user="root",
        ssh_options={"ProxyCommand": "/nix/store/xxx/bin/dumbpipe connect abc123"},
        host_key_check="accept-new",
    )
    env = remote.nix_ssh_env(control_master=False)
    opts = _parse_nix_sshopts(env)

    # The -o and its value must be separate tokens after splitting
    idx = opts.index("-o")
    assert opts[idx + 1] == "ProxyCommand=/nix/store/xxx/bin/dumbpipe connect abc123"


def test_nix_ssh_env_socks_proxy() -> None:
    """SOCKS proxy ProxyCommand must appear as a properly quoted option."""
    remote = Remote(
        address="test.onion",
        user="root",
        socks_port=9050,
    )
    env = remote.nix_ssh_env(control_master=False)
    opts = _parse_nix_sshopts(env)

    assert "-o" in opts
    proxy_opts = [
        opts[i + 1]
        for i, o in enumerate(opts)
        if o == "-o" and "ProxyCommand" in opts[i + 1]
    ]
    assert len(proxy_opts) == 1
    assert proxy_opts[0] == "ProxyCommand=nc -x localhost:9050 -X 5 %h %p"


def test_nix_ssh_env_control_master() -> None:
    """ControlMaster options must appear when requested."""
    with TemporaryDirectory() as td:
        remote = Remote(
            address="host",
            user="root",
            _control_path_dir=Path(td),
        )
        env = remote.nix_ssh_env(control_master=True)
        opts = _parse_nix_sshopts(env)

        assert "ControlMaster=auto" in opts
        assert "ControlPersist=1m" in opts
        assert f"ControlPath={Path(td) / 'socket'}" in opts


def test_nix_ssh_env_port_and_key() -> None:
    """Port and IdentityFile must be included."""
    remote = Remote(
        address="host",
        user="deploy",
        port=2222,
        private_key=Path("/tmp/my_key"),  # noqa: S108
    )
    env = remote.nix_ssh_env(control_master=False)
    opts = _parse_nix_sshopts(env)

    assert "-p" in opts
    assert opts[opts.index("-p") + 1] == "2222"
    assert "-i" in opts
    assert opts[opts.index("-i") + 1] == "/tmp/my_key"  # noqa: S108


def test_nix_ssh_env_host_key_none() -> None:
    """host_key_check='none' must disable checking and set /dev/null known hosts."""
    remote = Remote(
        address="host",
        user="root",
        host_key_check="none",
    )
    env = remote.nix_ssh_env(control_master=False)
    opts = _parse_nix_sshopts(env)

    assert "StrictHostKeyChecking=no" in opts
    assert "UserKnownHostsFile=/dev/null" in opts


def test_nix_ssh_env_forward_agent() -> None:
    """Forward agent flag must be present."""
    remote = Remote(
        address="host",
        user="root",
    )
    env = remote.nix_ssh_env(control_master=False)
    opts = _parse_nix_sshopts(env)

    assert "-A" in opts


def test_ssh_url_scheme() -> None:
    """ssh_url() must support custom schemes."""
    remote = Remote(address="myhost", user="deploy", port=2222)
    assert remote.ssh_url() == "ssh://deploy@myhost:2222"
    assert remote.ssh_url(scheme="ssh-ng") == "ssh-ng://deploy@myhost:2222"
