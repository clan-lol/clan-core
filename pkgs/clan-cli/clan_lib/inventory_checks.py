"""Service constraint checks evaluated from clanInternals.cliChecks.

Call `run_inventory_checks` before any operation that requires a valid
inventory (e.g. vars generate).  Warnings are logged; errors raise ClanError.
"""

import logging
from dataclasses import dataclass
from typing import TypedDict

from clan_lib.api import API
from clan_lib.errors import ClanError
from clan_lib.flake import Flake

log = logging.getLogger(__name__)


class InventoryCheck(TypedDict):
    id: str
    severity: str
    message: str


@dataclass
class CheckResult:
    checks: list[InventoryCheck]
    errors: list[InventoryCheck]
    warnings: list[InventoryCheck]


@API.register
def get_service_checks(flake: Flake) -> CheckResult:
    """Fetch cliChecks and partition by severity.  Always returns."""
    raw = flake.select("clanInternals.cliChecks")
    checks: list[InventoryCheck] = raw if isinstance(raw, list) else []

    errors = [c for c in checks if c.get("severity") == "error"]
    warnings = [c for c in checks if c.get("severity") == "warning"]

    return CheckResult(checks=checks, errors=errors, warnings=warnings)


def run_inventory_checks(flake: Flake) -> CheckResult:
    """Fetch cliChecks, log warnings, raise ClanError on errors."""
    result = get_service_checks(flake)
    for w in result.warnings:
        log.warning("[%s] %s", w["id"], w["message"])
    if result.errors:
        lines = "\n".join(f"  [{e['id']}] {e['message']}" for e in result.errors)
        msg = f"Inventory checks failed:\n{lines}"
        raise ClanError(msg)
    return result
