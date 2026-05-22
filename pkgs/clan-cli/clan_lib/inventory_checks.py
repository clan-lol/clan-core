"""Service constraint checks evaluated from clanInternals.cliChecks.

Call `run_inventory_checks` before any operation that requires a valid
inventory (e.g. vars generate).  Warnings are logged; errors raise ClanError.
"""

import logging
from dataclasses import dataclass

from clan_lib.errors import ClanError
from clan_lib.flake import Flake

log = logging.getLogger(__name__)


@dataclass
class CheckResult:
    checks: list[dict]
    errors: list[dict]
    warnings: list[dict]


def collect_inventory_checks(flake: Flake) -> CheckResult:
    """Fetch cliChecks and log warnings/errors.  Always returns."""
    raw = flake.select("clanInternals.cliChecks")
    checks: list[dict] = raw if isinstance(raw, list) else []

    errors = [c for c in checks if c.get("severity") == "error"]
    warnings = [c for c in checks if c.get("severity") == "warning"]

    for w in warnings:
        log.warning("[%s] %s", w.get("id", "?"), w.get("message", ""))

    for e in errors:
        log.error("[%s] %s", e.get("id", "?"), e.get("message", ""))

    return CheckResult(checks=checks, errors=errors, warnings=warnings)


def run_inventory_checks(flake: Flake) -> CheckResult:
    """Fetch cliChecks, log warnings/errors, raise ClanError on errors."""
    result = collect_inventory_checks(flake)
    if result.errors:
        ids = ", ".join(e.get("id", "?") for e in result.errors)
        msg = f"Inventory checks failed: {ids}"
        raise ClanError(msg)
    return result
