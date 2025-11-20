import ipaddress
import logging
import os
import re
import shlex
import subprocess
import sys
import urllib.parse
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from shlex import quote
from tempfile import TemporaryDirectory
from typing import TYPE_CHECKING

from clan_lib.cmd import CmdOut, RunOpts, run
from clan_lib.colors import AnsiColor
from clan_lib.errors import ClanError, indent_command  # Assuming these are available
from clan_lib.nix import nix_shell
from clan_lib.ssh.host_key import HostKeyCheck, hostkey_to_ssh_opts
from clan_lib.ssh.socks_wrapper import SocksWrapper
from clan_lib.ssh.sudo_askpass_proxy import SudoAskpassProxy

# Constants for URL parsing
EXPECTED_URL_PARTS = 2  # Expected parts when splitting on '?' or '='

if TYPE_CHECKING:
    from clan_lib.network.check import ConnectionOptions

cmdlog = logging.getLogger(__name__)

# Seconds until a message is printed when _run produces no output.
NO_OUTPUT_TIMEOUT = 20


@dataclass(frozen=True)
class Remote:
    address: str
    command_prefix: str | None = None
    user: str = "root"
    port: int | None = None
    private_key: Path | None = None
    password: str | None = None
    forward_agent: bool = True
    host_key_check: HostKeyCheck = "ask"
    verbose_ssh: bool = False
    ssh_options: dict[str, str] = field(default_factory=dict)
    socks_port: int | None = None
    socks_wrapper: SocksWrapper | None = None

    _control_path_dir: Path | None = None
    _askpass_path: str | None = None

    def __str__(self) -> str:
        return self.target

    def is_ipv6(self) -> bool:
        try:
            return isinstance(ipaddress.ip_address(self.address), ipaddress.IPv6Address)
        except ValueError:
            return False

    def override(
        self,
        *,
        user: str | None = None,
        address: str | None = None,
        host_key_check: HostKeyCheck | None = None,
        private_key: Path | None = None,
        password: str | None = None,
        socks_port: int | None = None,
        socks_wrapper: SocksWrapper | None = None,
        command_prefix: str | None = None,
        port: int | None = None,
        ssh_options: dict[str, str] | None = None,
    ) -> "Remote":
        """Returns a new Remote instance with the same data but with a different host_key_check."""
        return Remote(
            address=address or self.address,
            user=user or self.user,
            command_prefix=command_prefix or self.command_prefix,
            port=port or self.port,
            private_key=private_key if private_key is not None else self.private_key,
            password=password if password is not None else self.password,
            forward_agent=self.forward_agent,
            host_key_check=(
                host_key_check if host_key_check is not None else self.host_key_check
            ),
            verbose_ssh=self.verbose_ssh,
            ssh_options=ssh_options or self.ssh_options,
            socks_port=socks_port if socks_port is not None else self.socks_port,
            socks_wrapper=socks_wrapper
            if socks_wrapper is not None
            else self.socks_wrapper,
            _control_path_dir=self._control_path_dir,
            _askpass_path=self._askpass_path,
        )

    @property
    def target(self) -> str:
        return f"{self.user}@{self.address}"

    @classmethod
    def from_ssh_uri(
        cls,
        *,
        machine_name: str,
        address: str,
    ) -> "Remote":
        """Parse a deployment address and return a Remote object."""
        return _parse_ssh_uri(machine_name=machine_name, address=address)

    def run_local(
        self,
        cmd: list[str],
        opts: RunOpts | None = None,
        extra_env: dict[str, str] | None = None,
    ) -> CmdOut:
        """Command to run locally for the host"""
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
    def host_connection(self) -> Iterator["Remote"]:
        """Context manager to manage SSH ControlMaster connections.
        This will create a temporary directory for the control socket.
        """
        directory = None
        if sys.platform == "darwin" and os.environ.get("TMPDIR", "").startswith(
            "/var/folders/",
        ):
            directory = "/tmp/"  # noqa: S108 - Required on macOS due to bugs with default TMPDIR
        with TemporaryDirectory(prefix="clan-ssh", dir=directory) as temp_dir:
            remote = Remote(
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
                socks_port=self.socks_port,
                _control_path_dir=Path(temp_dir),
                _askpass_path=self._askpass_path,
            )
            try:
                yield remote
            finally:
                # Terminate the SSH master connection
                socket_path = Path(temp_dir) / "socket"
                if socket_path.exists():
                    try:
                        exit_cmd = [
                            "ssh",
                            "-o",
                            f"ControlPath={socket_path}",
                            "-O",
                            "exit",
                        ]
                        exit_cmd.append(remote.target)
                        subprocess.run(
                            exit_cmd,
                            check=False,
                            capture_output=True,
                            timeout=5,
                        )
                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                        # If exit fails still try to stop the master connection
                        pass

    @contextmanager
    def become_root(self) -> Iterator["Remote"]:
        """Context manager to set up sudo askpass proxy.
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
                socks_port=self.socks_port,
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
        """Internal method to run a command on the host via ssh.
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
                verbose_ssh=verbose_ssh,
                tty=tty,
                control_master=control_master,
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
            self._ssh_cmd_opts(control_master=control_master),  # Renamed
        )
        return env

    def _ssh_cmd_opts(
        self,
        control_master: bool = True,
    ) -> list[str]:
        ssh_opts = ["-A"] if self.forward_agent else []
        if self.port:
            ssh_opts.extend(["-p", str(self.port)])
        for k, v in self.ssh_options.items():
            ssh_opts.extend(["-o", f"{k}={shlex.quote(v)}"])
        ssh_opts.extend(hostkey_to_ssh_opts(self.host_key_check))
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
                    "ControlPersist=1m",
                    "-o",
                    f"ControlPath={socket_path}",
                ],
            )
        return ssh_opts

    def ssh_url(self) -> str:
        """Generates a standard SSH URL (ssh://[user@]host[:port])."""
        url = "ssh://"
        if self.user:
            url += f"{self.user}@"
        url += self.address
        if self.port:
            url += f":{self.port}"
        return url

    def ssh_cmd(
        self,
        verbose_ssh: bool = False,
        tty: bool = False,
        control_master: bool = True,
    ) -> list[str]:
        packages = []
        password_args = []
        if self.password:
            packages.append("sshpass")
            password_args = ["sshpass", "-p", self.password]

        current_ssh_opts = self._ssh_cmd_opts(control_master=control_master)
        if verbose_ssh or self.verbose_ssh:
            current_ssh_opts.extend(["-v"])
        if tty:
            current_ssh_opts.extend(["-t"])

        if self.socks_port:
            packages.append("netcat")
            current_ssh_opts.extend(
                [
                    "-o",
                    f"ProxyCommand=nc -x localhost:{self.socks_port} -X 5 %h %p",
                ],
            )

        cmd = [
            *password_args,
            "ssh",
            self.target,
            *current_ssh_opts,
        ]
        return nix_shell(packages, cmd)

    def _check_sshpass_errorcode(self, res: subprocess.CompletedProcess) -> None:
        """Check the return code of the sshpass command and raise an error if it indicates a failure.
        Error codes are based on man sshpass(1) and may vary by version.
        """
        if res.returncode == 0:
            return

        match res.returncode:
            case 1:
                msg = "Invalid command line argument"
                raise ClanError(msg)
            case 2:
                msg = "Conflicting arguments given"
                raise ClanError(msg)
            case 3:
                msg = "General runtime error"
                raise ClanError(msg)
            case 4:
                msg = "Unrecognized response from ssh (parse error)"
                raise ClanError(msg)
            case 5:
                msg = "Invalid/incorrect password"
                raise ClanError(msg)
            case 6:
                msg = "Host public key is unknown. sshpass exits without confirming the new key. Try using --host-key-heck none"
                raise ClanError(msg)
            case 7:
                msg = "IP public key changed. sshpass exits without confirming the new key."
                raise ClanError(msg)
            case _:
                msg = f"SSH command failed with return code {res.returncode}"
                raise ClanError(msg)

    def interactive_ssh(self, command: list[str] | None = None) -> None:
        ssh_cmd = self.ssh_cmd(tty=True, control_master=False)
        if command:
            ssh_cmd = [
                *self.ssh_cmd(tty=True, control_master=False),
                "--",
                "bash",
                "-c",
                quote('exec "$@"'),
                "--",
                " ".join(map(quote, command)),
            ]
        cmdlog.debug(
            f"{indent_command(ssh_cmd)}",
            extra={
                "command_prefix": self.command_prefix,
                "color": AnsiColor.GREEN.value,
            },
        )
        res = subprocess.run(ssh_cmd, check=False)

        # We only check the error code if a password is set, as sshpass is used.
        # AS sshpass swallows all output.
        if self.password:
            self._check_sshpass_errorcode(res)

    def check_machine_ssh_reachable(
        self,
        opts: "ConnectionOptions | None" = None,
    ) -> None:
        from clan_lib.network.check import check_machine_ssh_reachable  # noqa: PLC0415

        return check_machine_ssh_reachable(self, opts)

    def check_machine_ssh_login(self) -> None:
        from clan_lib.network.check import check_machine_ssh_login  # noqa: PLC0415

        return check_machine_ssh_login(self)


def _parse_ssh_uri(
    *,
    machine_name: str,
    address: str,
) -> "Remote":
    """Parses an SSH URI into a Remote object.
    The address can be in the form of:
    - `ssh://[user@]hostname[:port]?option=value&option2=value2`
    - `[user@]hostname[:port]`
    The specification can be found here: https://www.ietf.org/archive/id/draft-salowey-secsh-uri-00.html
    """
    address = address.removeprefix("ssh://")

    parts = address.split("?", maxsplit=1)
    endpoint, maybe_options = (
        parts if len(parts) == EXPECTED_URL_PARTS else (parts[0], "")
    )

    parts = endpoint.split("@")
    match len(parts):
        case 2:
            user, host_port = parts
        case 1:
            user, host_port = "root", parts[0]
        case _:
            msg = f"Invalid host, got `{address}` but expected something like `[user@]hostname[:port]`"
            raise ClanError(msg)

    # Make this check now rather than failing with a `ValueError`
    # when looking up the port from the `urlsplit` result below:
    if host_port.count(":") > 1 and not re.match(r".*\[.*]", host_port):
        msg = f"Invalid hostname: {address}. IPv6 addresses must be enclosed in brackets , e.g. [::1]"
        raise ClanError(msg)

    options: dict[str, str] = {}
    for o in maybe_options.split("&"):
        if len(o) == 0:
            continue
        parts = o.split("=", maxsplit=1)
        if len(parts) != EXPECTED_URL_PARTS:
            msg = (
                f"Invalid option in host `{address}`: option `{o}` does not have "
                f"a value (i.e. expected something like `name=value`)"
            )
            raise ClanError(msg)
        name, value = parts
        options[name] = value

    result = urllib.parse.urlsplit(f"//{host_port}")
    if not result.hostname:
        msg = f"Invalid host, got `{address}` but expected something like `[user@]hostname[:port]`"
        raise ClanError(msg)
    hostname = result.hostname
    port = result.port

    return Remote(
        address=hostname,
        user=user,
        port=port,
        command_prefix=machine_name,
        ssh_options=options,
    )
