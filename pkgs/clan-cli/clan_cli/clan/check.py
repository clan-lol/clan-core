import argparse
import json
import logging
import sys

from clan_lib.flake import require_flake

log = logging.getLogger(__name__)


def check_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    checks = flake.select("clanInternals.cliChecks")

    if not isinstance(checks, list):
        checks = []

    errors = [c for c in checks if c.get("severity") == "error"]
    warnings = [c for c in checks if c.get("severity") == "warning"]

    for w in warnings:
        log.warning("[%s] %s", w.get("id", "?"), w.get("message", ""))

    for e in errors:
        log.error("[%s] %s", e.get("id", "?"), e.get("message", ""))

    if args.json:
        json.dump(checks, sys.stdout, indent=2)
        print()

    if not checks:
        log.info("All checks passed.")
    elif errors:
        sys.exit(1)
