# ruff: noqa: SLF001
import logging
import os
import shlex
import socket
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from shlex import quote
from tempfile import TemporaryDirectory

from clan_cli.ssh.host_key import HostKeyCheck

from clan_lib.cmd import CmdOut, RunOpts, run
from clan_lib.colors import AnsiColor
from clan_lib.errors import ClanError  # Assuming these are available
from clan_lib.nix import nix_shell
from clan_lib.ssh.parse import parse_deployment_address

cmdlog = logging.getLogger(__name__)

# Seconds until a message is printed when _run produces no output.
NO_OUTPUT_TIMEOUT = 20


@dataclass(frozen=True)
class Remote:
    address: str
    user: str
    command_prefix: str
    port: int | None = None
    private_key: Path | None = None
    password: str | None = None
    forward_agent: bool = True
    host_key_check: HostKeyCheck = HostKeyCheck.ASK
    verbose_ssh: bool = False
    ssh_options: dict[str, str] = field(default_factory=dict)
    tor_socks: bool = False
    _control_path_dir: Path | None = None

    def __str__(self) -> str:
        return self.target

    @property
    def target(self) -> str:
        return f"{self.user}@{self.address}"

    @classmethod
    def with_user(cls, host: "Remote", user: str) -> "Remote":
        """
        Return a new Remote object with the specified user.
        """
        return cls(
            address=host.address,
            user=user,
            command_prefix=host.command_prefix,
            port=host.port,
            private_key=host.private_key,
            password=host.password,
            forward_agent=host.forward_agent,
            host_key_check=host.host_key_check,
            verbose_ssh=host.verbose_ssh,
            ssh_options=host.ssh_options,
            tor_socks=host.tor_socks,
        )

    @classmethod
    def from_deployment_address(
        cls,
        *,
        machine_name: str,
        address: str,
        host_key_check: HostKeyCheck,
        forward_agent: bool = True,
        private_key: Path | None = None,
    ) -> "Remote":
        """
        Parse a deployment address and return a Host object.
        """

        return parse_deployment_address(
            machine_name=machine_name,
            address=address,
            host_key_check=host_key_check,
            forward_agent=forward_agent,
            private_key=private_key,
        )

    def run_local(
        self,
        cmd: list[str],
        opts: RunOpts | None = None,
        extra_env: dict[str, str] | None = None,
    ) -> CmdOut:
        """
        Command to run locally for the host
        """
        if opts is None:
            opts = RunOpts()
        env = opts.env or os.environ.copy()
        if extra_env:
            env.update(extra_env)
        displayed_cmd = " ".join(cmd)
        cmdlog.info(
            f"$ {displayed_cmd}",
            extra={
                "command_prefix": self.command_prefix,
                "color": AnsiColor.GREEN.value,
            },
        )
        opts.env = env
        opts.prefix = self.command_prefix
        return run(cmd, opts)

    @contextmanager
    def ssh_control_master(self) -> Iterator["Remote"]:
        """
        Context manager to manage SSH ControlMaster connections.
        This will create a temporary directory for the control socket.
        """
        directory = None
        if sys.platform == "darwin" and os.environ.get("TMPDIR", "").startswith(
            "/var/folders/"
        ):
            directory = "/tmp/"
        # Use more specific prefix for the temp dir to avoid potential collisions if multiple hosts used
        prefix = f"clan-ssh-{self.address}-{self.port or 22}-{self.user}-"
        temp_dir = TemporaryDirectory(prefix=prefix, dir=directory)
        yield Remote(
            address=self.address,
            user=self.user,
            command_prefix=self.command_prefix,
            port=self.port,
            private_key=self.private_key,
            password=self.password,
            forward_agent=self.forward_agent,
            host_key_check=self.host_key_check,
            verbose_ssh=self.verbose_ssh,
            ssh_options=self.ssh_options,
            tor_socks=self.tor_socks,
            _control_path_dir=Path(temp_dir.name),
        )
        temp_dir.cleanup()

    def run(
        self,
        cmd: list[str],
        opts: RunOpts | None = None,
        become_root: bool = False,
        extra_env: dict[str, str] | None = None,
        tty: bool = False,
        verbose_ssh: bool = False,
        quiet: bool = False,
        control_master: bool = True,
    ) -> CmdOut:
        """
        Internal method to run a command on the host via ssh.
        `control_path_dir`: If provided, SSH ControlMaster options will be used.
        """
        if extra_env is None:
            extra_env = {}
        if opts is None:
            opts = RunOpts()

        sudo = ""
        if become_root and self.user != "root":
            sudo = "sudo -- "

        env_vars = []
        for k, v in extra_env.items():
            env_vars.append(f"{shlex.quote(k)}={shlex.quote(v)}")

        if opts.prefix is None:
            opts.prefix = self.command_prefix
        opts.needs_user_terminal = True
        if opts.cwd is not None:
            msg = "cwd is not supported for remote commands"
            raise ClanError(msg)

        displayed_cmd = ""
        export_cmd = ""
        if env_vars:
            export_cmd = f"export {' '.join(env_vars)}; "
            displayed_cmd += export_cmd
        displayed_cmd += " ".join(cmd)

        if not quiet:
            cmdlog.info(
                f"$ {displayed_cmd}",
                extra={
                    "command_prefix": self.command_prefix,
                    "color": AnsiColor.GREEN.value,
                },
            )

        bash_cmd = export_cmd
        if opts.shell:
            bash_cmd += " ".join(cmd)
            opts.shell = False
        else:
            bash_cmd += 'exec "$@"'

        ssh_cmd_list = self.ssh_cmd(
            verbose_ssh=verbose_ssh, tty=tty, control_master=control_master
        )
        ssh_cmd_list.extend(
            ["--", f"{sudo}bash -c {quote(bash_cmd)} -- {' '.join(map(quote, cmd))}"]
        )

        return run(ssh_cmd_list, opts)

    def nix_ssh_env(
        self,
        env: dict[str, str] | None = None,
        control_master: bool = True,
    ) -> dict[str, str]:
        if env is None:
            env = {}
        env["NIX_SSHOPTS"] = " ".join(
            self.ssh_cmd_opts(control_master=control_master)  # Renamed
        )
        return env

    def ssh_cmd_opts(
        self,
        control_master: bool = True,
    ) -> list[str]:
        effective_control_path_dir = self._control_path_dir
        if self._control_path_dir is None and not control_master:
            effective_control_path_dir = None
        elif self._control_path_dir is None and control_master:
            msg = "Control path directory is not set. Please with Remote.ssh_control_master() as ctx to set it."
            raise ClanError(msg)

        ssh_opts = ["-A"] if self.forward_agent else []
        if self.port:
            ssh_opts.extend(["-p", str(self.port)])
        for k, v in self.ssh_options.items():
            ssh_opts.extend(["-o", f"{k}={shlex.quote(v)}"])
        ssh_opts.extend(self.host_key_check.to_ssh_opt())
        if self.private_key:
            ssh_opts.extend(["-i", str(self.private_key)])

        if effective_control_path_dir:
            socket_path = (
                effective_control_path_dir
                / f"clan-{self.address}-{self.port or 22}-{self.user}"
            )
            ssh_opts.extend(["-o", "ControlPersist=30m"])
            ssh_opts.extend(["-o", f"ControlPath={socket_path}"])
            ssh_opts.extend(["-o", "ControlMaster=auto"])
        return ssh_opts

    def ssh_cmd(
        self, verbose_ssh: bool = False, tty: bool = False, control_master: bool = True
    ) -> list[str]:
        packages = []
        password_args = []
        if self.password:
            packages.append("sshpass")
            password_args = ["sshpass", "-p", self.password]

        current_ssh_opts = self.ssh_cmd_opts(control_master=control_master)
        if verbose_ssh or self.verbose_ssh:
            current_ssh_opts.extend(["-v"])
        if tty:
            current_ssh_opts.extend(["-t"])

        if self.tor_socks:
            packages.append("netcat")
            current_ssh_opts.extend(
                ["-o", "ProxyCommand=nc -x 127.0.0.1:9050 -X 5 %h %p"]
            )

        cmd = [
            *password_args,
            "ssh",
            self.target,
            *current_ssh_opts,
        ]
        return nix_shell(packages, cmd)

    def interactive_ssh(self) -> None:
        cmd_list = self.ssh_cmd(tty=True)
        subprocess.run(cmd_list)


def is_ssh_reachable(host: Remote) -> bool:
    address_family = socket.AF_INET6 if ":" in host.address else socket.AF_INET
    with socket.socket(address_family, socket.SOCK_STREAM) as sock:
        sock.settimeout(2)
        try:
            sock.connect((host.address, host.port or 22))
        except OSError:
            return False
        else:
            return True
