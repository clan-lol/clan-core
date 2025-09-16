"""Compatibility wrapper for relocated middleware components.

This module preserves the legacy import path ``clan_app.api.middleware`` while
the actual middleware implementations now live in ``clan_app.middleware``.
"""

from __future__ import annotations

from warnings import warn

import clan_app.middleware as _middleware
from clan_app.middleware import *  # noqa: F403

warn(
    "clan_app.api.middleware is deprecated; use clan_app.middleware instead",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = _middleware.__all__
