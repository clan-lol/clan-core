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
from clan_lib.ssh.sudo_askpass_proxy import SudoAskpassProxy

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
    _askpass_path: str | None = None

    def __str__(self) -> str:
        return self.target

    @property
    def target(self) -> str:
        return f"{self.user}@{self.address}"

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
        with TemporaryDirectory(prefix="clan-ssh", dir=directory) as temp_dir:
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
                _control_path_dir=Path(temp_dir),
                _askpass_path=self._askpass_path,
            )

    @contextmanager
    def become_root(self) -> Iterator["Remote"]:
        """
        Context manager to set up sudo askpass proxy.
        This will set up a proxy for sudo password prompts.
        """
        if self.user == "root":
            yield self
            return

        if (
            os.environ.get("DISPLAY")
            or os.environ.get("WAYLAND_DISPLAY")
            or sys.platform == "darwin"
        ):
            command = ["zenity", "--password", "--title", "%title%"]
            dependencies = ["zenity"]
        else:
            command = [
                "dialog",
                "--stdout",
                "--insecure",
                "--title",
                "%title%",
                "--passwordbox",
                "",
                "10",
                "50",
            ]
            dependencies = ["dialog"]
        proxy = SudoAskpassProxy(self, nix_shell(dependencies, command))
        try:
            askpass_path = proxy.run()
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
                _control_path_dir=self._control_path_dir,
                _askpass_path=askpass_path,
            )
        finally:
            proxy.cleanup()

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
        Internal method to run a command on the host via ssh.
        `control_path_dir`: If provided, SSH ControlMaster options will be used.
        """
        if extra_env is None:
            extra_env = {}
        if opts is None:
            opts = RunOpts()

        sudo = []
        if self._askpass_path is not None:
            sudo = [
                f"SUDO_ASKPASS={shlex.quote(self._askpass_path)}",
                "sudo",
                "-A",
                "--",
            ]

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

        ssh_cmd = [
            *self.ssh_cmd(
                verbose_ssh=verbose_ssh, tty=tty, control_master=control_master
            ),
            "--",
            *sudo,
            "bash",
            "-c",
            quote(bash_cmd),
            "--",
            " ".join(map(quote, cmd)),
        ]

        return run(ssh_cmd, opts)

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
        ssh_opts = ["-A"] if self.forward_agent else []
        if self.port:
            ssh_opts.extend(["-p", str(self.port)])
        for k, v in self.ssh_options.items():
            ssh_opts.extend(["-o", f"{k}={shlex.quote(v)}"])
        ssh_opts.extend(self.host_key_check.to_ssh_opt())
        if self.private_key:
            ssh_opts.extend(["-i", str(self.private_key)])

        if control_master:
            if self._control_path_dir is None:
                msg = "Bug! Control path directory is not set. Please use Remote.ssh_control_master() or set control_master to False."
                raise ClanError(msg)
            socket_path = self._control_path_dir / "socket"
            ssh_opts.extend(
                [
                    "-o",
                    "ControlMaster=auto",
                    "-o",
                    "ControlPersist=30m",
                    "-o",
                    f"ControlPath={socket_path}",
                ]
            )
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
        cmd_list = self.ssh_cmd(tty=True, control_master=False)
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
