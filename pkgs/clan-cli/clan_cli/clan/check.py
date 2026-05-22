import argparse
import json
import logging
import sys

from clan_lib.flake import require_flake
from clan_lib.inventory_checks import collect_inventory_checks

log = logging.getLogger(__name__)


def check_command(args: argparse.Namespace) -> None:
    flake = require_flake(args.flake)
    result = collect_inventory_checks(flake)

    if args.json:
        json.dump(result.checks, sys.stdout, indent=2)
        print()

    if not result.checks:
        log.info("All checks passed.")
    elif result.errors:
        sys.exit(1)
