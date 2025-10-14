"""Protocol definitions for platform-independent service management."""

import platform
from pathlib import Path
from typing import Protocol, runtime_checkable

from clan_lib.errors import ClanError

from .systemd_user import GroupedServiceInfo, ServiceInfo, ServiceStatus


@runtime_checkable
class ServiceManagerProtocol(Protocol):
    """Protocol for platform-independent service management backends."""

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
        """Start a service with the given configuration.

        Args:
            name: Service identifier
            command: Command and arguments to run
            working_dir: Working directory for the service
            env_vars: Environment variables for the service
            description: Human-readable service description
            autostart: Whether to enable service on boot
            group: Optional group name for service grouping

        Returns:
            Service name/identifier

        Raises:
            ClanError: If service creation or start fails

        """
        ...

    def stop_service(self, name: str) -> None:
        """Stop and remove a service.

        Args:
            name: Service identifier

        Raises:
            ClanError: If name is empty or operation fails

        """
        ...

    def get_status(self, name: str) -> ServiceStatus:
        """Get the current status of a service.

        Args:
            name: Service identifier

        Returns:
            Current service status

        Raises:
            ClanError: If name is empty

        """
        ...

    def restart_service(self, name: str) -> None:
        """Restart a service.

        Args:
            name: Service identifier

        Raises:
            ClanError: If name is empty or operation fails

        """
        ...

    def get_service_logs(self, name: str, lines: int = 50) -> str:
        """Get recent logs for a service.

        Args:
            name: Service identifier
            lines: Number of recent lines to retrieve

        Returns:
            Service logs as string

        Raises:
            ClanError: If name is empty

        """
        ...

    def list_running_services(self) -> list[ServiceInfo]:
        """List all services managed by this backend.

        Returns:
            List of service information dictionaries

        """
        ...

    def list_services_by_group(self, group: str) -> list[GroupedServiceInfo]:
        """List all services in the specified group.

        Args:
            group: Group name to filter by

        Returns:
            List of service information dictionaries for the group

        Raises:
            ClanError: If group name is empty

        """
        ...

    def stop_services_by_group(self, group: str) -> None:
        """Stop all services in the specified group.

        Args:
            group: Group name to stop services for

        Raises:
            ClanError: If group name is empty or operation fails

        """
        ...


def create_service_manager() -> ServiceManagerProtocol:
    """Create a platform-appropriate service manager.

    Returns:
        Service manager implementation for current platform

    Raises:
        ClanError: If platform is not supported

    """
    system = platform.system().lower()

    if system == "linux":
        from .systemd_user import SystemdUserService  # noqa: PLC0415

        return SystemdUserService(
            user_systemd_dir=Path.home() / ".config" / "systemd" / "user"
        )

    supported_platforms = ["linux"]
    msg = (
        f"Platform '{system}' is not supported. "
        f"Supported platforms: {', '.join(supported_platforms)}"
    )
    raise ClanError(msg)
