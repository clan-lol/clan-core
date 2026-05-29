"""Vars migrations that run before Nix evaluation."""

import logging
from pathlib import Path

from .zerotier import migrate_zerotier

log = logging.getLogger(__name__)


def run_migrations(clan_dir: Path) -> None:
    """Run all vars migrations. Called before Nix evaluation."""
    migrate_zerotier(clan_dir)
