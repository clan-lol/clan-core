"""Systemd user service runner abstraction.

This module provides a simple interface for managing systemd user services
based on command arrays. Each service is identified by a hash of the command,
allowing you to start/stop services using the same command that was used to create them.
"""

from .protocols import create_service_manager
from .systemd_user import SystemdUserService

__all__ = ["SystemdUserService", "create_service_manager"]
