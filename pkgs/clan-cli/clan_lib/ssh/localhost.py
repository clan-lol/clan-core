import logging
import os
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field

from clan_lib.cmd import CmdOut, RunOpts, run
from clan_lib.colors import AnsiColor
from clan_lib.ssh.host import Host

cmdlog = logging.getLogger(__name__)


@dataclass(frozen=True)
class LocalHost(Host):
    """
    A Host implementation that executes commands locally without SSH.
    """

    command_prefix: str = "localhost"
    _user: str = field(default_factory=lambda: os.environ.get("USER", "root"))
    _sudo: bool = False

    @property
    def target(self) -> str:
        """Return a descriptive target string for localhost."""
        return "localhost"

    @property
    def user(self) -> str:
        """Return the user for localhost."""
        return self._user

    def run(
        self,
        cmd: list[str],
        opts: RunOpts | None = None,
        extra_env: dict[str, str] | None = None,
        tty: bool = False,
        verbose_ssh: bool = False,
        quiet: bool = False,
        control_master: bool = True,
    ) -> CmdOut:
        """
        Run a command locally instead of via SSH.
        """
        if opts is None:
            opts = RunOpts()

        # Set up environment
        env = opts.env or os.environ.copy()
        if extra_env:
            env.update(extra_env)

        # Handle sudo if needed
        if self._sudo:
            # Prepend sudo command
            sudo_cmd = ["sudo", "-A", "--"]
            cmd = sudo_cmd + cmd

        # Set options
        opts.env = env
        opts.prefix = opts.prefix or self.command_prefix

        # Log the command
        displayed_cmd = " ".join(cmd)
        if not quiet:
            cmdlog.info(
                f"$ {displayed_cmd}",
                extra={
                    "command_prefix": self.command_prefix,
                    "color": AnsiColor.GREEN.value,
                },
            )

        # Run locally
        return run(cmd, opts)

    @contextmanager
    def become_root(self) -> Iterator["LocalHost"]:
        """
        Context manager to execute commands as root.
        """
        if self._user == "root":
            yield self
            return

        # This is a simplified version - could be enhanced with sudo askpass proxy.
        yield LocalHost(_sudo=True)

    @contextmanager
    def host_connection(self) -> Iterator["LocalHost"]:
        """
        For LocalHost, this is a no-op that just returns self.
        """
        yield self

    def nix_ssh_env(
        self,
        env: dict[str, str] | None = None,
        control_master: bool = True,
    ) -> dict[str, str]:
        """
        LocalHost doesn't need SSH environment variables.
        """
        if env is None:
            env = {}
        # Don't set NIX_SSHOPTS for localhost
        return env
