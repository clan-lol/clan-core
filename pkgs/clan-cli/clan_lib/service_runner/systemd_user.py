import shlex
import shutil
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypedDict

from clan_lib.cmd import RunOpts, run
from clan_lib.errors import ClanError

if TYPE_CHECKING:
    from clan_lib.errors import CmdOut

ServiceStatus = Literal["running", "stopped", "failed", "unknown"]


class ServiceInfo(TypedDict):
    """Information about a running service."""

    service_name: str
    status: str
    command: str
    unit_file: str


class GroupedServiceInfo(TypedDict):
    """Information about a service in a group."""

    service_name: str
    status: str
    command: str
    unit_file: str
    group: str


@dataclass(frozen=True)
class SystemdUserService:
    """Manages systemd user services using systemd-run for transient units."""

    user_systemd_dir: Path

    def __post_init__(self) -> None:
        self.user_systemd_dir.mkdir(parents=True, exist_ok=True)

    def _service_name(self, name: str) -> str:
        return f"service-runner-{name}"

    def _target_name(self, group: str) -> str:
        return f"service-runner-{group}"

    def _target_file_path(self, group: str) -> Path:
        return self.user_systemd_dir / f"{self._target_name(group)}.target"

    def _unit_file_path(self, name: str) -> Path:
        return self.user_systemd_dir / f"{self._service_name(name)}.service"

    def _validate_name(self, name: str, type_name: str = "Service") -> None:
        if not name:
            msg = f"{type_name} name cannot be empty"
            raise ClanError(msg)

    def _check_executable(self, command: list[str]) -> str:
        executable = shutil.which(command[0])
        if not executable:
            msg = f"Executable not found: {command[0]}"
            raise ClanError(msg)
        return executable

    def _systemctl(self, action: str, service_name: str) -> "CmdOut":
        """Run systemctl command with --user flag."""
        return run(
            ["systemctl", "--user", action, f"{service_name}.service"],
            RunOpts(check=False),
        )

    def _get_property(self, service_name: str, prop: str) -> str:
        """Get a systemd unit property value."""
        result = run(
            [
                "systemctl",
                "--user",
                "show",
                f"{service_name}.service",
                f"--property={prop}",
                "--no-pager",
            ],
            RunOpts(check=False),
        )
        prefix = f"{prop}="
        for line in result.stdout.split("\n"):
            if line.startswith(prefix):
                return line[len(prefix) :].strip()
        return ""

    def _create_target_file(self, group: str) -> None:
        """Create systemd target file for a group if it doesn't exist."""
        target_file = self._target_file_path(group)
        if target_file.exists():
            return

        content = textwrap.dedent(
            f"""
            [Unit]
            Description=Service runner group: {group}
            After=multi-user.target
            """
        )
        target_file.touch(exist_ok=True)
        target_file.chmod(0o600)
        target_file.write_text(content)
        run(["systemctl", "--user", "daemon-reload"])

    def _create_autostart_unit(
        self,
        name: str,
        command: list[str],
        working_dir: Path | None,
        env_vars: dict[str, str] | None,
        description: str | None,
        group: str | None,
    ) -> None:
        """Create persistent unit file for autostart services."""
        executable = self._check_executable(command)
        exec_start = f"{executable} {' '.join(shlex.quote(arg) for arg in command[1:])}"
        description = description or f"Service runner for {command[0]}"

        content = textwrap.dedent(
            f"""
            [Unit]
            Description={description}
            After=multi-user.target
            """
        )

        if group:
            content += f"PartOf={self._target_name(group)}.target\n"

        content += textwrap.dedent(
            f"""
            [Service]
            Type=simple
            ExecStart={exec_start}
            """
        )

        if working_dir:
            content += f"WorkingDirectory={working_dir}\n"

        for key, value in (env_vars or {}).items():
            content += f"Environment={key}={shlex.quote(value)}\n"

        content += textwrap.dedent(
            f"""
            [Install]
            WantedBy={self._target_name(group) if group else "default"}.target
            """
        )

        unit_file = self._unit_file_path(name)
        unit_file.touch(exist_ok=True)
        unit_file.chmod(0o600)
        unit_file.write_text(content)

    def start_service(
        self,
        name: str,
        command: list[str],
        working_dir: Path | None = None,
        env_vars: dict[str, str] | None = None,
        description: str | None = None,
        autostart: bool = False,
        group: str | None = None,
    ) -> str:
        """Start a systemd user service.

        autostart=False: Uses systemd-run (transient, no files).
        autostart=True: Creates unit files (persistent across reboots).
        """
        self._validate_name(name)
        if not command:
            msg = "Command cannot be empty"
            raise ClanError(msg)

        service_name = self._service_name(name)
        self._check_executable(command)

        if autostart:
            if group:
                self._create_target_file(group)
            self._create_autostart_unit(
                name, command, working_dir, env_vars, description, group
            )
            run(["systemctl", "--user", "daemon-reload"])

            result = self._systemctl("enable", service_name)
            if result.returncode != 0:
                msg = f"Failed to enable service: {result.stderr}"
                raise ClanError(msg)

            result = self._systemctl("start", service_name)
            if result.returncode != 0:
                msg = f"Failed to start service: {result.stderr}"
                raise ClanError(msg)
        else:
            # Use systemd-run for transient services
            desc = description or f"Service runner for {command[0]}"
            cmd = [
                "systemd-run",
                "--user",
                f"--unit={service_name}",
                f"--description={desc}",
            ]

            if working_dir:
                cmd.append(f"--working-directory={working_dir}")

            for key, value in (env_vars or {}).items():
                cmd.append(f"--setenv={key}={value}")

            if group:
                self._create_target_file(group)
                cmd.append(f"--property=PartOf={self._target_name(group)}.target")

            cmd.extend(command)

            result = run(cmd, RunOpts(check=False))
            if result.returncode != 0:
                msg = f"Failed to start service: {result.stderr}"
                raise ClanError(msg)

        return name

    def stop_service(self, name: str) -> None:
        """Stop a systemd user service."""
        self._validate_name(name)
        service_name = self._service_name(name)

        result = self._systemctl("stop", service_name)
        if result.returncode != 0 and "not loaded" not in result.stderr.lower():
            msg = f"Failed to stop service: {result.stderr}"
            raise ClanError(msg)

        self._systemctl("disable", service_name)  # Ignore errors for transient units

        unit_file = self._unit_file_path(name)
        if unit_file.exists():
            unit_file.unlink(missing_ok=True)
            run(["systemctl", "--user", "daemon-reload"], RunOpts(check=False))

    def get_status(self, name: str) -> ServiceStatus:
        """Get the status of a service."""
        self._validate_name(name)
        result = self._systemctl("is-active", self._service_name(name))
        status_map: dict[str, ServiceStatus] = {
            "active": "running",
            "inactive": "stopped",
            "failed": "failed",
        }
        return status_map.get(result.stdout.strip(), "unknown")

    def restart_service(self, name: str) -> None:
        """Restart a service."""
        self._validate_name(name)
        result = self._systemctl("restart", self._service_name(name))
        if result.returncode != 0:
            msg = f"Failed to restart service: {result.stderr}"
            raise ClanError(msg)

    def get_service_logs(self, name: str, lines: int = 50) -> str:
        """Get recent logs for a service."""
        self._validate_name(name)
        result = run(
            [
                "journalctl",
                "--user",
                "-u",
                f"{self._service_name(name)}.service",
                "-n",
                str(lines),
                "--no-pager",
            ]
        )
        return result.stdout

    def _get_service_info(self, unit_name: str) -> tuple[str, str, str]:
        """Get status, command, and unit file for a service."""
        status = self._get_property(unit_name, "ActiveState")
        command = self._get_property(unit_name, "ExecStart")
        fragment_path = self._get_property(unit_name, "FragmentPath")

        # Transient units are stored in /run/user/.../systemd/transient/
        if not fragment_path or "/transient/" in fragment_path:
            unit_file = "(transient)"
        else:
            unit_file = fragment_path

        return status, command, unit_file

    def list_running_services(self) -> list[ServiceInfo]:
        """List all service-runner services."""
        result = run(
            [
                "systemctl",
                "--user",
                "list-units",
                "service-runner-*.service",
                "--all",
                "--no-legend",
                "--no-pager",
                "--plain",
            ],
            RunOpts(check=False),
        )

        services: list[ServiceInfo] = []
        # systemctl list-units format: UNIT LOAD ACTIVE SUB DESCRIPTION
        min_required_fields = 4
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue

            parts = line.split(None, 4)
            if len(parts) < min_required_fields:
                continue

            unit_name = parts[0].replace(".service", "")
            if not unit_name.startswith("service-runner-"):
                continue

            status, command, unit_file = self._get_service_info(unit_name)
            services.append(
                {
                    "service_name": unit_name,
                    "status": status,
                    "command": command,
                    "unit_file": unit_file,
                }
            )

        return services

    def list_services_by_group(self, group: str) -> list[GroupedServiceInfo]:
        """List all services in a group."""
        self._validate_name(group, "Group")

        if not self._target_file_path(group).exists():
            return []

        result = run(
            [
                "systemctl",
                "--user",
                "list-dependencies",
                f"{self._target_name(group)}.target",
                "--plain",
            ],
            RunOpts(check=False),
        )

        services: list[GroupedServiceInfo] = []
        for raw_line in result.stdout.split("\n"):
            line = raw_line.strip()
            if not (line.endswith(".service") and line.startswith("service-runner-")):
                continue

            service_name = line.replace(".service", "")
            status, command, unit_file = self._get_service_info(service_name)
            services.append(
                {
                    "service_name": service_name,
                    "status": status,
                    "command": command,
                    "unit_file": unit_file,
                    "group": group,
                }
            )

        return services

    def stop_services_by_group(self, group: str) -> None:
        """Stop all services in a group."""
        self._validate_name(group, "Group")

        target_file = self._target_file_path(group)
        if not target_file.exists():
            return

        services = self.list_services_by_group(group)

        # Stop the target (stops all PartOf services)
        result = run(
            ["systemctl", "--user", "stop", f"{self._target_name(group)}.target"],
            RunOpts(check=False),
        )
        if result.returncode != 0:
            msg = f"Failed to stop target: {result.stderr}"
            raise ClanError(msg)

        # Disable and remove unit files for non-transient services
        for service in services:
            if service["unit_file"] != "(transient)":
                self._systemctl("disable", service["service_name"])
                Path(service["unit_file"]).unlink(missing_ok=True)

        target_file.unlink(missing_ok=True)
        run(["systemctl", "--user", "daemon-reload"], RunOpts(check=False))
