import os
import shlex
import shutil
import textwrap
from collections.abc import Generator
from contextlib import contextmanager, suppress
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal

from clan_lib.cmd import RunOpts, run
from clan_lib.errors import ClanError

if TYPE_CHECKING:
    from clan_lib.errors import CmdOut

ServiceStatus = Literal["running", "stopped", "failed", "unknown"]


@dataclass(frozen=True)
class SystemdUserService:
    """Manages systemd user services by name"""

    user_systemd_dir: Path

    def __post_init__(self) -> None:
        self.user_systemd_dir.mkdir(parents=True, exist_ok=True)

    def _service_name(self, name: str) -> str:
        """Generate service name from given name"""
        return f"service-runner-{name}"

    def _unit_file_path(self, name: str) -> Path:
        """Get the path to the systemd unit file for this service name"""
        service_name = self._service_name(name)
        return self.user_systemd_dir / f"{service_name}.service"

    @contextmanager
    def _cleanup_on_error(self, unit_file: Path) -> Generator[None]:
        """Context manager to clean up created files if an exception occurs"""
        try:
            yield
        except Exception:
            # Clean up the unit file if it was created
            if unit_file.exists():
                with suppress(OSError):
                    unit_file.unlink()
            raise

    def _create_unit_file(
        self,
        name: str,
        command: list[str],
        working_dir: Path | None = None,
        env_vars: dict[str, str] | None = None,
        description: str | None = None,
        autostart: bool = False,
    ) -> Path:
        """Create systemd unit file for the given command"""
        unit_file = self._unit_file_path(name)

        with self._cleanup_on_error(unit_file):
            executable = shutil.which(command[0])
            if not executable:
                msg = f"Executable not found: {command[0]}"
                raise ClanError(msg)
            exec_start = f"{executable} {' '.join(command[1:])}"

            if not description:
                description = f"Service runner for {shlex.quote(command[0])}"

            unit_content = textwrap.dedent(
                f"""
                [Unit]
                Description="{description}"
                After=multi-user.target

                [Service]
                Type=simple
                ExecStart={exec_start}
            """
            )

            if working_dir:
                unit_content += f"WorkingDirectory={working_dir}\n"

            if env_vars:
                for key, value in env_vars.items():
                    # Properly quote the value for systemd
                    quoted_value = shlex.quote(value)
                    unit_content += f"Environment={key}={quoted_value}\n"

            if autostart:
                unit_content += textwrap.dedent(
                    """
                    [Install]
                    WantedBy=default.target
                """
                )

            unit_file.touch(exist_ok=True)
            unit_file.chmod(0o600)
            with unit_file.open("w") as f:
                f.write(unit_content)

        return unit_file

    def _run_systemctl(self, action: str, service_name: str) -> "CmdOut":
        """Run systemctl command with --user flag"""
        cmd = ["systemctl", "--user", action, f"{service_name}.service"]
        return run(cmd, RunOpts(check=False))

    def start_service(
        self,
        name: str,
        command: list[str],
        working_dir: Path | None = None,
        extra_env_vars: dict[str, str] | None = None,
        description: str | None = None,
        autostart: bool = False,
    ) -> str:
        """Start a systemd user service for the given command.
        Returns the service name.
        """
        if not command:
            msg = "Command cannot be empty"
            raise ClanError(msg)
        if not name:
            msg = "Service name cannot be empty"
            raise ClanError(msg)

        service_name = self._service_name(name)

        # Collect essential environment variables for user services
        env_vars = {}

        # Essential variables that user services typically need
        essential_vars = [
            "PATH",
            "HOME",
            "USER",
            "LOGNAME",
            "XDG_CONFIG_HOME",
            "XDG_DATA_HOME",
            "XDG_CACHE_HOME",
            "XDG_RUNTIME_DIR",
            "XDG_SESSION_ID",
            "XDG_SESSION_TYPE",
            "DBUS_SESSION_BUS_ADDRESS",
            "SSH_AUTH_SOCK",
            "SSH_AGENT_PID",
            "GPG_AGENT_INFO",
            "GNUPGHOME",
        ]

        # Add essential vars if they exist in the current environment
        for var in essential_vars:
            value = os.environ.get(var)
            if value is not None:
                env_vars[var] = value

        # Allow extra_env_vars to override defaults
        env_vars.update(extra_env_vars or {})

        # Create the unit file
        self._create_unit_file(
            name, command, working_dir, env_vars, description, autostart
        )

        run(["systemctl", "--user", "daemon-reload"])

        # Enable the service only if autostart is True
        if autostart:
            result = self._run_systemctl("enable", service_name)
            if result.returncode != 0:
                msg = f"Failed to enable service: {result.stderr}"
                raise ClanError(msg)

        # Start the service
        result = self._run_systemctl("start", service_name)
        if result.returncode != 0:
            msg = f"Failed to start service: {result.stderr}"
            raise ClanError(msg)

        return name

    def stop_service(self, name: str) -> bool:
        """Stop the systemd user service for the given name.
        Returns True if successful, False otherwise.
        """
        if not name:
            msg = "Service name cannot be empty"
            raise ClanError(msg)

        service_name = self._service_name(name)

        # Stop the service
        result = self._run_systemctl("stop", service_name)
        if result.returncode != 0:
            return False

        # Disable the service
        result = self._run_systemctl("disable", service_name)
        if result.returncode != 0:
            return False

        # Remove the unit file
        unit_file = self._unit_file_path(name)
        try:
            unit_file.unlink(missing_ok=True)
        except OSError:
            return False

        run(["systemctl", "--user", "daemon-reload"], RunOpts(check=False))

        return True

    def get_status(self, name: str) -> ServiceStatus:
        """Get the status of the service for the given name"""
        if not name:
            msg = "Service name cannot be empty"
            raise ClanError(msg)

        service_name = self._service_name(name)

        # Check if unit file exists
        unit_file = self._unit_file_path(name)
        if not unit_file.exists():
            return "unknown"

        result = self._run_systemctl("is-active", service_name)
        status_output = result.stdout.strip()

        if status_output == "active":
            return "running"
        if status_output == "inactive":
            return "stopped"
        if status_output == "failed":
            return "failed"
        return "unknown"

    def restart_service(self, name: str) -> bool:
        """Restart the service for the given name"""
        if not name:
            msg = "Service name cannot be empty"
            raise ClanError(msg)

        service_name = self._service_name(name)

        result = self._run_systemctl("restart", service_name)
        return result.returncode == 0

    def get_service_logs(self, name: str, lines: int = 50) -> str:
        """Get recent logs for the service"""
        if not name:
            msg = "Service name cannot be empty"
            raise ClanError(msg)

        service_name = self._service_name(name)

        cmd = [
            "journalctl",
            "--user",
            "-u",
            f"{service_name}.service",
            "-n",
            str(lines),
            "--no-pager",
        ]
        result = run(cmd, RunOpts(check=False))
        if result.returncode == 0:
            return result.stdout
        return f"Failed to get logs: {result.stderr}"

    def list_running_services(self) -> list[dict[str, Any]]:
        """List all running service-runner services"""
        services = []

        # Get all service files
        for unit_file in self.user_systemd_dir.glob("service-runner-*.service"):
            service_name = unit_file.stem

            # Get status
            result = self._run_systemctl("is-active", service_name)
            status = result.stdout.strip()

            # Try to extract command from unit file
            try:
                with unit_file.open() as f:
                    content = f.read()
                    # Simple parsing - look for ExecStart line
                    for line in content.split("\n"):
                        if line.startswith("ExecStart="):
                            exec_start = line[10:]  # Remove "ExecStart="
                            services.append(
                                {
                                    "service_name": service_name,
                                    "status": status,
                                    "command": exec_start,
                                    "unit_file": str(unit_file),
                                }
                            )
                            break
            except OSError:
                continue

        return services
