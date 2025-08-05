"""Base Host interface for both local and remote command execution."""

import logging
from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from clan_lib.cmd import CmdOut, RunOpts

cmdlog = logging.getLogger(__name__)


@dataclass(frozen=True)
class Host(ABC):
    """
    Abstract base class for host command execution.
    This provides a common interface for both local and remote hosts.
    """

    command_prefix: str

    @property
    @abstractmethod
    def target(self) -> str:
        """Return a descriptive target string for this host."""

    @property
    @abstractmethod
    def user(self) -> str:
        """Return the user for this host."""

    @abstractmethod
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
        Run a command on the host.

        Args:
            cmd: Command to execute
            opts: Run options
            extra_env: Additional environment variables
            tty: Whether to allocate a TTY (for remote hosts)
            verbose_ssh: Enable verbose SSH output (for remote hosts)
            quiet: Suppress command logging
            control_master: Use SSH ControlMaster (for remote hosts)

        Returns:
            Command output
        """

    @contextmanager
    @abstractmethod
    def become_root(self) -> Iterator["Host"]:
        """
        Context manager to execute commands as root.
        """

    @contextmanager
    @abstractmethod
    def host_connection(self) -> Iterator["Host"]:
        """
        Context manager to manage host connections.
        For remote hosts, this manages SSH ControlMaster connections.
        For local hosts, this is a no-op that returns self.
        """

    @abstractmethod
    def nix_ssh_env(
        self,
        env: dict[str, str] | None = None,
        control_master: bool = True,
    ) -> dict[str, str]:
        """
        Get environment variables for Nix operations.
        Remote hosts will add NIX_SSHOPTS, local hosts won't.
        """
